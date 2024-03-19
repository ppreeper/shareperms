#!/usr/bin/env python3
import subprocess
import argparse
import yaml


def getfiles(directory, perms):
    c = "setfacl"
    r = "-R"
    b = "-b"
    d = "-d"
    m = "-m"
    cmd = []
    cmd.append([c, r, b, directory])
    if perms["groups"] is not None:
        for v in perms["groups"]:
            domain = v.get("domain")
            name = v.get("name")
            if len(domain) > 0:
                name = domain + "\\" + name
            p = f"""group:{name}:{v['permission']}"""
            cmd.append([c, r, d, m, p, directory])
            cmd.append([c, r, m, p, directory])
    if perms["users"] is not None:
        for v in perms["users"]:
            domain = v.get("domain")
            name = v.get("name")
            if len(domain) > 0:
                name = domain + "\\" + name
            p = f"""user:{name}:{v['permission']}"""
            cmd.append([c, r, d, m, p, directory])
            cmd.append([c, r, m, p, directory])
    if perms["other"] is not None:
        p = f"""other::{perms["other"]}"""
        cmd.append([c, r, d, m, p, directory])
        cmd.append([c, r, m, p, directory])
    fs = {}
    fs["dir"] = directory
    fs["cmds"] = cmd
    return fs


def main():
    parser = argparse.ArgumentParser("Apply permissions to share folder")
    parser.add_argument(
        "-n",
        "--no-op",
        action="store_true",
        dest="debug",
        default=False,
        help="no operation, show output",
    )
    parser.add_argument(
        "-s",
        "--share",
        action="store",
        dest="share",
        default="",
        help="share to update",
    )
    parser.add_argument(
        "-c",
        "--config",
        action="store",
        dest="config",
        default="/etc/shareperms.yaml",
        help="share permissions",
    )
    args = parser.parse_args()

    with open(args.config) as f:
        shares = yaml.safe_load(f)

    fh = {}
    # Gather share permissions
    if args.share == "":
        for s in shares["shares"]:
            fh[s["name"]] = s["directory"]
    else:
        for s in shares["shares"]:
            if args.share in s["name"]:
                fh[s["name"]] = s["directory"]
    fh = dict(sorted(fh.items(), key=lambda item: item[1]))

    # Gather commands
    cmds = []
    for f in sorted(fh.keys()):
        for s in shares["shares"]:
            if f == s["name"]:
                cmds.append(getfiles(s["directory"], s["perms"]))

    # Execute commands
    for c in cmds:
        d = c.get("dir")
        cc = c.get("cmds")
        clen = len(cc)
        print(f"Applying permissions to: {d}")
        for i in range(len(cc)):
            p = i / clen
            print("\rApplying permissions: {0:.2%} ".format(p), end="", flush=True)
            if args.debug:
                print(cc[i])
            else:
                subprocess.call(cc[i])
        print("\rApplying permissions {0:.0%} complete".format(1), flush=True)


if __name__ == "__main__":
    main()
