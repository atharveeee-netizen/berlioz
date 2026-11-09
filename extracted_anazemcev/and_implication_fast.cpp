// SPDX-License-Identifier: Apache-2.0
// Exact, fixed-qubit-id KMB v2 transitive-AND pass, C++17.
//
// Boolean implication algorithm: Kozykorpesh's Apache-2.0 exact_compile.py,
// https://www.kaggle.com/code/kozykappa/quantum-ai-compact-arithmetic-banked-qrom?scriptVersionId=361456406
// Binary compiler integration and globally-clean conditional facts follow our
// src/dqi_portfolio_v2.py. Compiled decoder provenance remains k256.dev:
// https://www.kaggle.com/code/k256net/claude?scriptVersionId=361337610
//
// Only CCX is rewritten (CX, X, or deletion). Every other instruction, including
// all phases, resets, measurements, classical writes and conditions, keeps its
// order and operands. Registers, quantum IDs, rotations and INFO bytes persist.
// Scratch starts zero; registered quantum inputs are unknown. Facts require
// unchanged per-logical-wire epochs. Local facts are discarded at every POP;
// facts created from a target zero on ALL active/inactive branches survive POP.
// Full official semantic verification is still required for real candidates.

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <functional>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

using U8 = std::uint8_t;
using U32 = std::uint32_t;
using U64 = std::uint64_t;
using Value = std::int8_t;
constexpr Value UNKNOWN = -1;

static U32 u32(const U8* p) {
    return U32(p[0]) | (U32(p[1]) << 8) | (U32(p[2]) << 16) | (U32(p[3]) << 24);
}
static U64 u64(const U8* p) {
    return U64(u32(p)) | (U64(u32(p + 4)) << 32);
}
static void put64(U8* p, U64 v) {
    for (int k = 0; k < 8; ++k) p[k] = U8(v >> (8 * k));
}
static Value xorr(Value a, Value b) {
    return a == UNKNOWN || b == UNKNOWN ? UNKNOWN : Value(a ^ b);
}
static Value product(Value a, Value b) {
    if (a == 0 || b == 0) return 0;
    if (a == 1 && b == 1) return 1;
    return UNKNOWN;
}

struct Packet { std::size_t offset = 0, length = 0; };
struct Kmb {
    std::vector<U8> bytes;
    std::array<U64, 9> counts{};
    std::array<Packet, 12> packets{};
    U32 width = 0, bits = 0, registers = 0;
    std::size_t register_end = 104;
    std::vector<U8> protected_q;

    explicit Kmb(const std::string& path) {
        std::ifstream f(path, std::ios::binary | std::ios::ate);
        if (!f) throw std::runtime_error("cannot open source");
        auto size = f.tellg();
        if (size < 104) throw std::runtime_error("truncated KMB header");
        bytes.resize(std::size_t(size));
        f.seekg(0);
        if (!f.read(reinterpret_cast<char*>(bytes.data()), bytes.size()))
            throw std::runtime_error("failed reading source");
        const U8 magic[16] = {0xd7,0x50,0xc7,0xd5,0xc3,0x29,0xd3,0x26,
                             0xe3,0xcc,0x9f,0x68,0x34,0xf2,0xb8,0xbf};
        if (std::memcmp(bytes.data(), magic, 16) || u32(bytes.data() + 16) != 2)
            throw std::runtime_error("expected Kickmix KMB version 2");
        width = u32(bytes.data() + 20);
        bits = u32(bytes.data() + 24);
        registers = u32(bytes.data() + 28);
        protected_q.assign(width, 0);
        for (int k = 0; k < 9; ++k) counts[k] = u64(bytes.data() + 32 + 8 * k);
        std::size_t pos = 104;
        auto check = [&](std::size_t p, U64 n) {
            if (p > bytes.size() || n > bytes.size() - p)
                throw std::runtime_error("truncated or oversized KMB packet");
        };
        for (U32 k = 0; k < registers; ++k) {
            check(pos, 16);
            const U64 kind = u64(bytes.data() + pos), length = u64(bytes.data() + pos + 8);
            pos += 16; check(pos, length);
            if (kind || length < 8) throw std::runtime_error("invalid register packet");
            const U32 namesize = u32(bytes.data() + pos), targets = u32(bytes.data() + pos + 4);
            if (U64(8) + namesize + U64(4) * targets != length)
                throw std::runtime_error("inconsistent register packet");
            for (U32 j = 0; j < targets; ++j) {
                const U32 target = u32(bytes.data() + pos + 8 + namesize + 4 * std::size_t(j));
                if (target & 0x80000000u) {
                    const U32 q = target & 0x7fffffffu;
                    if (q >= width) throw std::runtime_error("register qubit exceeds width");
                    protected_q[q] = 1;
                }
            }
            pos += std::size_t(length);
        }
        register_end = pos;
        for (U64 kind = 1; kind <= 11; ++kind) {
            check(pos, 16);
            const U64 actual = u64(bytes.data() + pos), length = u64(bytes.data() + pos + 8);
            pos += 16; check(pos, length);
            if (kind != actual) throw std::runtime_error("unexpected column packet kind");
            packets[kind] = {pos, std::size_t(length)};
            pos += std::size_t(length);
        }
        if (pos != bytes.size()) throw std::runtime_error("trailing KMB bytes");
        const std::array<U64, 11> lengths = {
            counts[0], counts[1]*4, counts[1]*4, counts[1]*4,
            counts[2]*4, counts[2]*4, counts[3]*4,
            counts[4]*4, counts[5]*4, counts[6]*16,
            (counts[7]+1)*8 + counts[8]
        };
        for (int k = 1; k <= 11; ++k)
            if (packets[k].length != lengths[k-1])
                throw std::runtime_error("header count does not match packet length");
    }
    U32 operand(int column, U64 index) const {
        const auto& p = packets[column];
        if (index >= p.length / 4) throw std::runtime_error("operand column exhausted");
        return u32(bytes.data() + p.offset + 4 * std::size_t(index));
    }
};

struct Fact {
    bool valid = false, global = false;
    U8 ncontrols = 0;
    U64 target_epoch = 0, local_generation = 0;
    std::array<U32,2> control{};
    std::array<U64,2> epoch{};
};

int main(int argc, char** argv) {
    try {
        if (argc < 3) throw std::runtime_error(
            "usage: and_implication_fast source.kmb target.kmb [--facts=both|global|local|none] [--no-rewrite]");
        const std::string source = argv[1], destination = argv[2];
        if (source == destination) throw std::runtime_error("source and destination must differ");
        bool global_facts = true, local_facts = true, rewrite = true;
        for (int k = 3; k < argc; ++k) {
            const std::string arg = argv[k];
            if (arg == "--no-rewrite") rewrite = false;
            else if (arg == "--facts=both") { global_facts = true; local_facts = true; }
            else if (arg == "--facts=global") { global_facts = true; local_facts = false; }
            else if (arg == "--facts=local") { global_facts = false; local_facts = true; }
            else if (arg == "--facts=none") { global_facts = false; local_facts = false; }
            else throw std::runtime_error("unknown argument: " + arg);
        }
        const auto start = std::chrono::steady_clock::now();
        const U32 endian = 1;
        if (*reinterpret_cast<const U8*>(&endian) != 1)
            throw std::runtime_error("this build currently writes on little-endian hosts only");
        Kmb in(source);
        std::vector<Value> values(in.width, 0);
        for (U32 q = 0; q < in.width; ++q) if (in.protected_q[q]) values[q] = UNKNOWN;
        std::vector<std::vector<Value>> stack;
        std::vector<U64> epochs(in.width, 0), visited(in.width, 0);
        std::vector<Fact> facts(in.width);
        U64 local_generation = 1, traversal = 0;
        std::function<bool(U32,U32)> search = [&](U32 a, U32 b) -> bool {
            if (a == b || values[b] == 1 || values[a] == 0) return true;
            if (visited[a] == traversal) return false;
            visited[a] = traversal;
            const Fact& fact = facts[a];
            if (!fact.valid || fact.target_epoch != epochs[a] ||
                (!fact.global && fact.local_generation != local_generation)) return false;
            for (U8 j = 0; j < fact.ncontrols; ++j)
                if (fact.epoch[j] != epochs[fact.control[j]]) return false;
            for (U8 j = 0; j < fact.ncontrols; ++j)
                if (fact.control[j] == b || search(fact.control[j], b)) return true;
            return false;
        };
        auto implies = [&](U32 a, U32 b) { ++traversal; return search(a, b); };
        auto globally_zero = [&](U32 q) {
            if (values[q] != 0) return false;
            for (const auto& old : stack) if (old[q] != 0) return false;
            return true;
        };
        std::vector<U8> types;
        types.reserve(std::size_t(in.counts[0]));
        std::array<std::vector<U32>, 10> columns;
        for (int k = 2; k < 10; ++k) columns[k].reserve(in.packets[k].length / 4);
        U64 n1i=0, n2i=0, n3i=0, bi=0, ci=0;
        U64 zero_drop=0, constant_x=0, one_cx=0, and_cx=0, globals_created=0, locals_created=0;
        U64 input_ccx=0, output_ccx=0;
        std::array<U64,256> frequencies{};
        const U8* input_types = in.bytes.data() + in.packets[1].offset;
        for (U64 number = 0; number < in.counts[0]; ++number) {
            const U8 raw = input_types[number], op = raw & 0x7f;
            const U8 nq = (raw >> 4) & 3;
            const bool conditional = raw & 0x80;
            std::array<U32,3> qs{};
            if (nq == 3) {
                qs = {in.operand(2,n3i), in.operand(3,n3i), in.operand(4,n3i)}; ++n3i;
            } else if (nq == 2) {
                qs = {in.operand(5,n2i), in.operand(6,n2i), 0}; ++n2i;
            } else if (nq == 1) {
                qs[0] = in.operand(7,n1i++);
            }
            for (U8 j = 0; j < nq; ++j)
                if (qs[j] >= in.width) throw std::runtime_error("qubit exceeds declared width");
            const U32 bit = (raw & 0x40) ? in.operand(8,bi++) : 0;
            const U32 condition = conditional ? in.operand(9,ci++) : 0;
            if (((raw & 0x40) && bit >= in.bits) || (conditional && condition >= in.bits))
                throw std::runtime_error("classical bit exceeds declared width");
            if (raw == 0x81) stack.push_back(values);
            else if (raw == 1) {
                if (stack.empty()) throw std::runtime_error("unbalanced POP_CONDITION");
                const auto& old = stack.back();
                for (U32 q = 0; q < in.width; ++q)
                    if (values[q] != old[q]) values[q] = UNKNOWN;
                stack.pop_back();
                ++local_generation;
            }
            const bool target_zero = (op == 0x21 || op == 0x31) && values[qs[nq-1]] == 0;
            const bool target_global_zero = target_zero && globally_zero(qs[nq-1]);
            int newop = op;
            U8 newnq = nq;
            auto newqs = qs;
            if (op == 0x31) {
                ++input_ccx;
                const U32 a=qs[0], b=qs[1], t=qs[2];
                if (a == b || a == t || b == t) throw std::runtime_error("aliased CCX operands");
                if (rewrite) {
                    if (values[a] == 0 || values[b] == 0) {
                        newop = -1; ++zero_drop;
                    } else if (values[a] == 1 && values[b] == 1) {
                        newop = 0x11; newnq=1; newqs={t,0,0}; ++constant_x;
                    } else if (values[a] == 1) {
                        newop = 0x21; newnq=2; newqs={b,t,0}; ++one_cx;
                    } else if (values[b] == 1) {
                        newop = 0x21; newnq=2; newqs={a,t,0}; ++one_cx;
                    } else if (implies(a,b)) {
                        newop = 0x21; newnq=2; newqs={a,t,0}; ++and_cx;
                    } else if (implies(b,a)) {
                        newop = 0x21; newnq=2; newqs={b,t,0}; ++and_cx;
                    }
                }
            }
            std::array<U32,3> writes{};
            std::array<Value,3> result{};
            U8 nwrites = 0;
            if (op == 0x31) {
                writes[0]=qs[2]; result[0]=xorr(values[qs[2]],product(values[qs[0]],values[qs[1]])); nwrites=1;
            } else if (op == 0x21) {
                writes[0]=qs[1]; result[0]=xorr(values[qs[1]],values[qs[0]]); nwrites=1;
            } else if (op == 0x11) {
                writes[0]=qs[0]; result[0]=xorr(values[qs[0]],1); nwrites=1;
            } else if (op == 0x12 || op == 0x50) {
                writes[0]=qs[0]; result[0]=0; nwrites=1;
            } else if (op == 0x22) {
                writes[0]=qs[0]; writes[1]=qs[1]; result[0]=values[qs[1]]; result[1]=values[qs[0]]; nwrites=2;
            } else if (op == 0x32) {
                const Value c=values[qs[0]], a=values[qs[1]], b=values[qs[2]];
                writes[0]=qs[1]; writes[1]=qs[2]; nwrites=2;
                result[0] = c == 0 || a == b ? a : (c == 1 ? b : UNKNOWN);
                result[1] = c == 0 || a == b ? b : (c == 1 ? a : UNKNOWN);
            } else if (op == 0 || op == 1 || op == 6 || op == 7 || op == 0x10 ||
                       op == 0x13 || op == 0x17 || op == 0x20 || op == 0x30 ||
                       op == 0x40 || op == 0x41 || op == 0x42 || op == 0x47) {
                // Phase, debug, classical and scope operations do not change Boolean qubit values.
            } else {
                for (U8 j=0; j<nq; ++j) { writes[j]=qs[j]; result[j]=UNKNOWN; }
                nwrites=nq;
            }
            for (U8 j=0; j<nwrites; ++j) {
                const U32 q=writes[j];
                values[q] = !conditional || values[q] == result[j] ? result[j] : UNKNOWN;
                ++epochs[q]; facts[q].valid=false;
            }
            if (newop == 0x21 || newop == 0x31) {
                const bool global = global_facts && target_global_zero;
                const bool local = local_facts && !conditional && target_zero;
                if (global || local) {
                    const U32 target=newqs[newnq-1];
                    bool alias=false;
                    for (U8 j=0; j<newnq-1; ++j) alias |= newqs[j] == target;
                    if (!alias) {
                        Fact fact; fact.valid=true; fact.global=global;
                        fact.ncontrols=newnq-1; fact.target_epoch=epochs[target];
                        fact.local_generation=local_generation;
                        for (U8 j=0; j<fact.ncontrols; ++j) {
                            fact.control[j]=newqs[j]; fact.epoch[j]=epochs[newqs[j]];
                        }
                        facts[target]=fact;
                        if (global) ++globals_created; else ++locals_created;
                    }
                }
            }
            if (newop < 0) continue;
            const U8 outtype=U8(newop) | (raw & 0x80);
            types.push_back(outtype); ++frequencies[outtype];
            if (newop == 0x31) ++output_ccx;
            if (newnq == 3) {
                columns[2].push_back(newqs[0]); columns[3].push_back(newqs[1]); columns[4].push_back(newqs[2]);
            } else if (newnq == 2) {
                columns[5].push_back(newqs[0]); columns[6].push_back(newqs[1]);
            } else if (newnq == 1) columns[7].push_back(newqs[0]);
            if (raw & 0x40) columns[8].push_back(bit);
            if (raw & 0x80) columns[9].push_back(condition);
        }
        if (!stack.empty()) throw std::runtime_error("unbalanced condition stack at EOF");
        if (n3i != in.counts[1] || n2i != in.counts[2] || n1i != in.counts[3] ||
            bi != in.counts[4] || ci != in.counts[5]) throw std::runtime_error("operand cursors disagree with header");
        if (frequencies[0x13]+frequencies[0x93] != in.counts[6] || frequencies[6] != in.counts[7])
            throw std::runtime_error("rotation or info count mismatch");
        auto counts=in.counts;
        counts[0]=types.size(); counts[1]=columns[2].size(); counts[2]=columns[5].size();
        counts[3]=columns[7].size(); counts[4]=columns[8].size(); counts[5]=columns[9].size();
        std::array<U8,104> header{};
        std::copy_n(in.bytes.begin(),104,header.begin());
        for (int k=0;k<9;++k) put64(header.data()+32+8*k,counts[k]);
        std::ofstream out(destination,std::ios::binary|std::ios::trunc);
        if (!out) throw std::runtime_error("cannot open destination");
        out.write(reinterpret_cast<const char*>(header.data()),header.size());
        out.write(reinterpret_cast<const char*>(in.bytes.data()+104),in.register_end-104);
        auto packet = [&](U64 kind, const void* data, std::size_t length) {
            std::array<U8,16> h{}; put64(h.data(),kind); put64(h.data()+8,length);
            out.write(reinterpret_cast<const char*>(h.data()),h.size());
            if (length) out.write(reinterpret_cast<const char*>(data),length);
        };
        packet(1,types.data(),types.size());
        for (int k=2;k<=9;++k) packet(k,columns[k].data(),columns[k].size()*4);
        for (int k=10;k<=11;++k) packet(k,in.bytes.data()+in.packets[k].offset,in.packets[k].length);
        out.close();
        if (!out) throw std::runtime_error("failed writing candidate");
        const double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
        std::cout << "{\"num_qubits\":" << in.width << ",\"num_bits\":" << in.bits
                  << ",\"input_ops\":" << in.counts[0] << ",\"output_ops\":" << counts[0]
                  << ",\"input_ccx\":" << input_ccx << ",\"output_ccx\":" << output_ccx
                  << ",\"removed_static_toffoli\":" << input_ccx-output_ccx
                  << ",\"rewrites\":{\"zero_control_toffoli\":" << zero_drop
                  << ",\"constant_toffoli\":" << constant_x
                  << ",\"one_control_toffoli\":" << one_cx
                  << ",\"transitive_and_implication\":" << and_cx
                  << "},\"global_facts_created\":" << globals_created
                  << ",\"local_facts_created\":" << locals_created
                  << ",\"global_facts_enabled\":" << (global_facts?"true":"false")
                  << ",\"local_facts_enabled\":" << (local_facts?"true":"false")
                  << ",\"seconds\":" << seconds
                  << ",\"verification_status\":\"UNVERIFIED; fresh full official verification required\"}\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "and_implication_fast: " << error.what() << '\n';
        return 1;
    }
}