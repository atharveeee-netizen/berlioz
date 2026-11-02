import time, sys
from kaggle.api.kaggle_api_extended import KaggleApi

api = KaggleApi()
api.authenticate()
competition = 'google-verifiable-quantum-circuit-compilation'

subs = api.competition_submissions(competition)
latest = subs[0]
ref = getattr(latest, 'ref', None)
desc = getattr(latest, 'description', '')
print(f"[*] Tracking submission ref {ref}: {desc}")

for step in range(30):
    subs = api.competition_submissions(competition)
    s = subs[0]
    status = str(getattr(s, 'status', ''))
    score = getattr(s, 'public_score', None) or getattr(s, 'publicScore', None)
    now = time.strftime('%H:%M:%S')
    print(f"[{now}] Poll {step:2d} | Status: {status} | Public Score: {score}", flush=True)
    if 'COMPLETE' in status.upper():
        print(f"\n=======================================================")
        print(f"[+] SUBMISSION OFFICIALLY GRADED: {score}")
        print(f"=======================================================")
        sys.exit(0)
    elif 'ERROR' in status.upper():
        err = getattr(s, 'errorDescription', 'unknown')
        print(f"[-] Submission error: {err}")
        sys.exit(1)
    time.sleep(15)

print("[!] Polling timed out. Check Kaggle UI or run again.")

