
#!/usr/bin/env python3
"""
Advanced uploader simulator:
- Multiple users (admin, auditor1, compliance1)
- Random sleep between uploads
- Random assignment to controls
- Tracks success/failure
"""
import os, json, time, random, argparse, requests

USERS = [
    ("admin","adminpass"),
    ("auditor1","adminpass"),
    ("compliance1","adminpass")
]

def login(api, username, password):
    url = api.rstrip("/") + "/api/login"
    r = requests.post(url, json={"username":username, "password":password})
    if r.status_code == 200:
        j = r.json()
        print(f"[+] Logged in: {username}")
        return j["token"]
    print("[-] LOGIN FAIL:", r.text)
    return None

def upload(api, token, file_path, cid):
    url = api.rstrip("/") + "/api/evidence/upload"
    headers = {"Authorization":"Bearer "+token}
    files = {"file":open(file_path,"rb")}
    data = {"control_id":str(cid)}
    r = requests.post(url, headers=headers, files=files, data=data)
    try: out = r.json()
    except: out = r.text
    return r.status_code, out

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--api", default="http://127.0.0.1:5000")
    args = p.parse_args()

    base = os.path.dirname(os.path.realpath(__file__))
    mf = os.path.join(base, "manifest.json")
    manifest = json.load(open(mf))

    # load evidence files
    evidence = [x for x in manifest]

    # simulate uploads
    for item in evidence:
        user = random.choice(USERS)
        token = login(args.api, user[0], user[1])
        if not token:
            continue

        path = os.path.join(base,"evidence_files",item["filename"])
        cid = item["control_id"]

        print(f"[*] {user[0]} uploading {item['filename']} -> control {cid}")
        status, resp = upload(args.api, token, path, cid)
        print(f"    => {status}: {resp}")

        # random delay
        time.sleep(random.uniform(0.3,1.2))

if __name__=="__main__":
    main()
