# LANE E PLAN: CHEMISTRY ANF & GAUGE POLISH
**Hypothesis:** Applying an exact Voodoo gauge transform and SO60 column polish to the Double Factorization matrix reduces lambda_eff without altering angle circuits.
**Price:** 1% cost reduction = 0.483 in lambda_eff = 162.7 Toffolis.
**Approaches Evaluated:** (1) J=7 linear QROM (explodes Toffolis to 15,400, dropping ratio to 6.92x); (2) R=10 expanded precision (explodes width and tables, dropping ratio to 4.94x); (3) Voodoo gauge transform + SO60 column polish on R=8 J=5 Banked ANF.
**Test:** Official double factorization energy verifier (chemical accuracy limit 20.000 mHa).
**Kill Rule:** Kill if error exceeds 20.000 mHa or Q_angle exceeds 128.
**Outcome:** LANDED. lambda_eff improved from 48.3236 to 48.2992; chemical accuracy satisfied; ratio improved to 9.93301x.
