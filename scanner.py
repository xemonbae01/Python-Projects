import os
import subprocess
import sys
import time
import re

x = {
    "com.android.systemui", "com.google.android.gms", "com.android.settings",
    "com.google.android.permissioncontroller", "com.google.android.overlay.modules.permissioncontroller",
    "com.google.android.overlay.modules.permissioncontroller.forframework",
    "com.google.android.federatedcompute"
}
y = {
    "com.spy.soft", "com.flexispy.android", "com.mspy.android", "com.hoverwatch",
    "com.thetruthspy", "com.cocospy", "com.xnspy", "com.mobiletracker",
    "com.ikeymonitor", "com.highster.mobile", "com.stealthgenie", "com.phoneguardian",
    "com.reptilicus", "com.android.system.update", "com.google.service.update",
    "com.system.service", "com.android.system.core", "com.security.service",
    "com.spyic", "com.minspy", "com.eyespy", "com.trackview", "com.cerberus",
    "com.android.system.service", "com.remote.control.android"
}
z = ["/sdcard", "/storage/emulated/0", "/storage/emulated/0/Android/data"]
uno = ["ps", "-A"]
hell = ["pm", "list", "packages", "-f"]
dih = re.compile(
    r"(spy(?:ware|soft|app|ic)?|keylog(?:ger)?|stealthgenie|flexispy|mspy|hoverwatch|"
    r"thetruthspy|cocospy|xnspy|mobiletracker|ikeymonitor|highster|phoneguardian|"
    r"reptilicus|minspy|eyespy|trackview|cerberusapp|remote[\._-]?access|rat[\._-]?client)",
    re.I
)
oem = (
    "com.android.", "com.google.", "com.mediatek.", "com.transsion.", "com.qualcomm.",
    "com.samsung.", "com.miui.", "com.huawei.", "com.oppo.", "com.vivo.", "com.realme.",
    "com.oneplus.", "com.nothing.", "com.motorola.", "com.sony.", "com.lge.",
    "com.goodix.", "com.jiiov.", "com.hoffnung.", "com.imaging.", "android"
)
cat = []
pookie = []

def get_running():
    try:
        out = subprocess.check_output(uno, stderr=subprocess.DEVNULL).decode(errors="ignore")
        return out.splitlines()
    except Exception:
        return []

def get_packages():
    try:
        out = subprocess.check_output(hell, stderr=subprocess.DEVNULL).decode(errors="ignore")
        return [line.strip() for line in out.splitlines() if line.strip()]
    except Exception:
        try:
            out = subprocess.check_output(["cmd", "package", "list", "packages"], stderr=subprocess.DEVNULL).decode(errors="ignore")
            return [line.strip() for line in out.splitlines() if line.strip()]
        except Exception:
            return []

def deep_walk(root):
    found = []
    try:
        for dirpath, _, filenames in os.walk(root):
            for f in filenames:
                full = os.path.join(dirpath, f)
                if dih.search(f) or dih.search(dirpath):
                    found.append(full)
    except Exception:
        pass
    return found

def is_oem(pkg):
    return any(pkg.startswith(p) or pkg == p for p in oem)

def scan():
    print("[*] surface scan started")
    time.sleep(0.25)
    print("[*] process table")
    procs = get_running()
    for line in procs:
        if dih.search(line):
            cat.append(("PROCESS", line.strip()))
    print(f"[+] processes: {len(procs)}")

    print("[*] package list")
    pkgs = get_packages()
    for p in pkgs:
        pkg = p.split("=")[-1] if "=" in p else p.replace("package:", "").strip()
        if pkg in y:
            cat.append(("KNOWN_SPYWARE", pkg))
        elif dih.search(pkg):
            cat.append(("PACKAGE", pkg))
        if not is_oem(pkg) and pkg not in x:
            pookie.append(pkg)
    print(f"[+] packages: {len(pkgs)}")

    print("[*] path walk (sdcard only, no root)")
    for root in z:
        if os.path.exists(root) and os.access(root, os.R_OK):
            for h in deep_walk(root):
                cat.append(("FILE", h))
    print("[+] path pass done")

    print("\n" + "=" * 48)
    print("SCAN RESULT")
    print("=" * 48)
    if not cat:
        print("[OK] no strong spyware indicators")
    else:
        print(f"[!] {len(cat)} hits:")
        for kind, item in sorted(set(cat)):
            print(f"  [{kind}] {item}")
    clean = sorted(set(pookie))
    if clean:
        print(f"\n[i] non-oem third-party packages: {len(clean)}")
        for p in clean[:50]:
            print(f"  - {p}")
        if len(clean) > 50:
            print(f"  ... +{len(clean)-50} more")
    print("\n[!] heuristic only — not a full AV engine")
    print("[!] root + real scanner needed for deep detection")
    print("[!] review anything flagged manually")

if __name__ == "__main__":
    scan()
