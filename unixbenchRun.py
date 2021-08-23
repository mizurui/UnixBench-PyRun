#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##############################################################
# UnixBench - Release 5.1.3, based on:
# The BYTE UNIX Benchmarks - Release 3
#         Module: Run   SID: 3.11 5/15/91 19:30:14
# Original Byte benchmarks written by:
#       Ben Smith,              Tom Yager at BYTE Magazine
#       ben@bytepb.byte.com     tyager@bytepb.byte.com
# BIX:  bensmith                tyager
#
# Compatible to Python script was written by:
#       Ruilx Alxa  GT-Soft Studio
#
##############################################################
# General Purpose Benchmark
# based on the work by Ken McDonell,
#                         Computer Science, Monash University
##############################################################

import argparse
import math
import os
import re
import stat
import subprocess
import sys
import time

#####################
# Configuration
#####################
version = "5.1.3"
language = "en_US.utf8"
longIterCount = 10
shortIterCount = 3
cCompiler = "gcc"
BASEDIR = os.getcwd().strip()


def getDir(var, default):
    val = os.getenv(var, default)
    wd = os.getcwd()
    if not os.path.exists(val):
        os.mkdir(val)
    os.chdir(val)
    val = os.getcwd()
    os.chdir(wd)
    os.environ[var] = val
    return val


BINDIR = getDir('UB_BINDIR', os.path.join(BASEDIR, "pgms"))
TMPDIR = getDir('UB_TMPDIR', os.path.join(BASEDIR, "tmp"))
RESULTDIR = getDir('UB_RESULTDIR', os.path.join(BASEDIR, "results"))
TESTDIR = getDir('UB_TESTDIR', os.path.join(BASEDIR, "testdir"))

# Test Specifications
testCats = {
    'system': {'name': "System Benchmarks", 'maxCopies': 16},
    '2d': {'name': "2D Graphics Benchmarks", 'maxCopies': 1},
    '3d': {'name': "3D Graphics Benchmarks", 'maxCopies': 1},
    'misc': {'name': "Non-Index Benchmarks", 'maxCopies': 16},
}
arithmetic = [
    "arithoh", "short", "int", "long", "float", "double", "whetstone-double"
]
fs = [
    "fstime-w", "fstime-r", "fstime",
    "fsbuffer-w", "fsbuffer-r", "fsbuffer",
    "fsdisk-w", "fsdisk-r", "fsdisk"
]
oldsystem = [
    "execl", "fstime", "fsbuffer", "fsdisk", "pipe", "context1", "spawn",
    "syscall"
]
system = [
    "shell1", "shell8", "shell16"
]
system.extend(oldsystem)
index = [
    "dhry2reg", "whetstone-double"
]
index.extend(oldsystem)
index.extend(["shell1", "shell8"])
graphics = [
    "2d-rects", "2d-ellipse", "2d-aashapes", "2d-text", "2d-blit",
    "2d-window", "ubgears"
]

testList = {
    # Individual tests.
    "dhry2reg": None,
    "whetstone-double": None,
    "syscall": None,
    "pipe": None,
    "context1": None,
    "spawn": None,
    "execl": None,
    "fstime-w": None,
    "fstime-r": None,
    "fstime": None,
    "fsbuffer-w": None,
    "fsbuffer-r": None,
    "fsbuffer": None,
    "fsdisk-w": None,
    "fsdisk-r": None,
    "fsdisk": None,
    "shell1": None,
    "shell8": None,
    "shell16": None,
    "short": None,
    "int": None,
    "long": None,
    "float": None,
    "double": None,
    "arithoh": None,
    "C": None,
    "dc": None,
    "hanoi": None,
    "grep": None,
    "sysexec": None,

    "2d-rects": None,
    "2d-lines": None,
    "2d-circle": None,
    "2d-ellipse": None,
    "2d-shapes": None,
    "2d-aashapes": None,
    "2d-polys": None,
    "2d-text": None,
    "2d-blit": None,
    "2d-window": None,

    "ubgears": None,

    "arithmetic": arithmetic,
    "dhry": ["dhry2reg"],
    "dhrystone": ["dhry2reg"],
    "whets": ["whetstone-double"],
    "whetstone": ["whetstone-double"],
    "load": ["shell"],
    "misc": ["C", "dc", "hanoi"],
    "speed": [arithmetic, system],
    "oldsystem": oldsystem,
    "system": system,
    "fs": fs,
    "shell": ["shell1", "shell8", "shell16"],
    "graphics": graphics,

    "index": index,

    "gindex": [index, graphics]
}

baseParams = {
    "prog": None,
    "options": "",
    "repeat": "short",
    "stdout": 1,
    "stdin": "",
    "logmsg": "",
}

testParams = {
    "dhry2reg": {
        "logmsg": "Dhrystone 2 using register variables",
        "cat": 'system',
        "options": "10",
        "repeat": 'long',
    },
    "whetstone-double": {
        "logmsg": "Double-Precision Whetstone",
        "cat": 'system',
        "repeat": 'long',
    },
    "syscall": {
        "logmsg": "System Call Overhead",
        "cat": 'system',
        "repeat": 'long',
        "options": "10",
    },
    "context1": {
        "logmsg": "Pipe-based Context Switching",
        "cat": 'system',
        "repeat": 'long',
        "options": "10",
    },
    "pipe": {
        "logmsg": "Pipe Throughput",
        "cat": 'system',
        "repeat": 'long',
        "options": "10",
    },
    "spawn": {
        "logmsg": "Process Creation",
        "cat": 'system',
        "options": "30",
    },
    "execl": {
        "logmsg": "Execl Throughput",
        "cat": 'system',
        "options": "30",
    },
    "fstime-w": {
        "logmsg": "File Write 1024 bufsize 2000 maxblocks",
        "cat": 'system',
        "prog": os.path.join(BINDIR, "fstime"),
        "options": f"-w -t 30 -d \"{TMPDIR}\" -b 1024 -m 2000",
    },
    "fstime-r": {
        "logmsg": "File Read 1024 bufsize 2000 maxblocks",
        "cat": 'system',
        "prog": os.path.join(BINDIR, "fstime"),
        "options": f"-r -t 30 -d \"{TMPDIR}\" -b 1024 -m 2000",
    },
    "fstime": {
        "logmsg": "File Copy 1024 bufsize 2000 maxblocks",
        "cat": 'system',
        "prog": os.path.join(BINDIR, "fstime"),
        "options": f"-c -t 30 -d \"{TMPDIR}\" -b 1024 -m 2000",
    },
    "fsbuffer-w": {
        "logmsg": "File Write 256 bufsize 500 maxblocks",
        "cat": 'system',
        "prog": os.path.join(BINDIR, "fstime"),
        "options": f"-w -t 30 -d \"{TMPDIR}\" -b 256 -m 500",
    },
    "fsbuffer-r": {
        "logmsg": "File Read 256 bufsize 500 maxblocks",
        "cat": 'system',
        "prog": os.path.join(BINDIR, "fstime"),
        "options": f"-r -t 30 -d \"{TMPDIR}\" -b 256 -m 500",
    },
    "fsbuffer": {
        "logmsg": "File Copy 256 bufsize 500 maxblocks",
        "cat": 'system',
        "prog": os.path.join(BINDIR, "fstime"),
        "options": f"-c -t 30 -d \"{TMPDIR}\" -b 256 -m 500",
    },
    "fsdisk-w": {
        "logmsg": "File Write 4096 bufsize 8000 maxblocks",
        "cat": 'system',
        "prog": os.path.join(BINDIR, "fstime"),
        "options": f"-w -t 30 -d \"{TMPDIR}\" -b 4096 -m 8000",
    },
    "fsdisk-r": {
        "logmsg": "File Read 4096 bufsize 8000 maxblocks",
        "cat": 'system',
        "prog": os.path.join(BINDIR, "fstime"),
        "options": f"-r -t 30 -d \"{TMPDIR}\" -b 4096 -m 8000",
    },
    "fsdisk": {
        "logmsg": "File Copy 4096 bufsize 8000 maxblocks",
        "cat": 'system',
        "prog": os.path.join(BINDIR, "fstime"),
        "options": f"-c -t 30 -d \"{TMPDIR}\" -b 4096 -m 8000",
    },
    "shell1": {
        "logmsg": "Shell Scripts (1 concurrent)",
        "cat": 'system',
        "prog": os.path.join(BINDIR, "looper"),
        "options": f"60 \"{os.path.join(BINDIR, 'multi.sh')}\" 1",
    },
    "shell8": {
        "logmsg": "Shell Scripts (8 concurrent)",
        "cat": 'system',
        "prog": os.path.join(BINDIR, "looper"),
        "options": f"60 \"{os.path.join(BINDIR, 'multi.sh')}\" 8",
    },
    "shell16": {
        "logmsg": "Shell Scripts (16 concurrent)",
        "cat": 'system',
        "prog": os.path.join(BINDIR, "looper"),
        "options": f"60 \"{os.path.join(BINDIR, 'multi.sh')}\" 16",
    },
    "2d-rects": {
        "logmsg": "2D graphics: rectangles",
        "cat": '2d',
        "prog": os.path.join(BINDIR, "gfx-x11"),
        "options": "rects 3 2",
    },
    "2d-lines": {
        "logmsg": "2D graphics: lines",
        "cat": '2d',
        "prog": os.path.join(BINDIR, "gfx-x11"),
        "options": "lines 3 2",
    },
    "2d-circle": {
        "logmsg": "2D graphics: circles",
        "cat": '2d',
        "prog": os.path.join(BINDIR, "gfx-x11"),
        "options": "circle 3 2",
    },
    "2d-ellipse": {
        "logmsg": "2D graphics: ellipses",
        "cat": '2d',
        "prog": os.path.join(BINDIR, "gfx-x11"),
        "options": "ellipse 3 2",
    },
    "2d-shapes": {
        "logmsg": "2D graphics: polygons",
        "cat": '2d',
        "prog": os.path.join(BINDIR, "gfx-x11"),
        "options": "shapes 3 2",
    },
    "2d-aashapes": {
        "logmsg": "2D graphics: aa polygons",
        "cat": '2d',
        "prog": os.path.join(BINDIR, "gfx-x11"),
        "options": "aashapes 3 2",
    },
    "2d-polys": {
        "logmsg": "2D graphics: complex polygons",
        "cat": '2d',
        "prog": os.path.join(BINDIR, "gfx-x11"),
        "options": "polys 3 2",
    },
    "2d-text": {
        "logmsg": "2D graphics: text",
        "cat": '2d',
        "prog": os.path.join(BINDIR, "gfx-x11"),
        "options": "text 3 2",
    },
    "2d-blit": {
        "logmsg": "2D graphics: images and blits",
        "cat": '2d',
        "prog": os.path.join(BINDIR, "gfx-x11"),
        "options": "blit 3 2",
    },
    "2d-window": {
        "logmsg": "2D graphics: windows",
        "cat": '2d',
        "prog": os.path.join(BINDIR, "gfx-x11"),
        "options": "window 3 2",
    },
    "ubgears": {
        "logmsg": "3D graphics: gears",
        "cat": '3d',
        "options": "-time 20 -v",
    },

    "C": {
        "logmsg": f"C Compiler Throughput ({cCompiler})",
        "cat": 'misc',
        "prog": os.path.join(BINDIR, "looper"),
        "options": f"60 {cCompiler} cctest.c",
    },
    "arithoh": {
        "logmsg": "Arithoh",
        "cat": 'misc',
        "options": "10",
    },
    "short": {
        "logmsg": "Arithmetic Test (short)",
        "cat": 'misc',
        "options": "10",
    },
    "int": {
        "logmsg": "Arithmetic Test (int)",
        "cat": 'misc',
        "options": "10",
    },
    "long": {
        "logmsg": "Arithmetic Test (long)",
        "cat": 'misc',
        "options": "10",
    },
    "float": {
        "logmsg": "Arithmetic Test (float)",
        "cat": 'misc',
        "options": "10",
    },
    "double": {
        "logmsg": "Arithmetic Test (double)",
        "cat": 'misc',
        "options": "10",
    },
    "dc": {
        "logmsg": "Dc: sqrt(2) to 99 decimal places",
        "cat": 'misc',
        "prog": os.path.join(BINDIR, "looper"),
        "options": "30 dc",
        "stdin": "dc.dat",
    },
    "hanoi": {
        "logmsg": "Recursion Test -- Tower of Hanoi",
        "cat": 'misc',
        "options": "20",
    },
    "grep": {
        "logmsg": "Grep a large file (system's grep)",
        "cat": 'misc',
        "prog": os.path.join(BINDIR, "looper"),
        "options": "30 grep -c gimp large.txt",
    },
    "sysexec": {
        "logmsg": "Exec System Call Overhead",
        "cat": 'misc',
        "repeat": 'long',
        "prog": os.path.join(BINDIR, "syscall"),
        "options": "10 exec",
    },
}

x86CpuFlags = {
    'pae': "Physical Address Ext",
    'sep': "SYSENTER/SYSEXIT",
    'syscall': "SYSCALL/SYSRET",
    'mmx': "MMX",
    'mmxext': "AMD MMX",
    'cxmmx': "Cyrix MMX",
    'xmm': "Streaming SIMD",
    'xmm2': "Streaming SIMD-2",
    'xmm3': "Streaming SIMD-3",
    'ht': "Hyper-Threading",
    'ia64': "IA-64 processor",
    'lm': "x86-64",
    'vmx': "Intel virtualization",
    'svm': "AMD virtualization",
}


# Utilities

def command(cmd):
    process = subprocess.Popen(cmd,
                               bufsize=0,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               shell=True)
    pid = process.pid
    return pid, process


def getCmdOutput(cmd):
    timeout = 300
    pid, process = command(cmd)
    returnCode = process.wait(timeout)
    if process.poll() != 0:
        process.terminate()
        raise RuntimeError(f"Process '{process.pid}' ran timeout({timeout}s)")
    stdout = process.stdout.read().strip()
    return stdout.decode('utf-8')


def logFile_(sysInfo):
    count = 1
    ymd = time.strftime("%Y-%m-%d")

    while True:
        log = os.path.join(RESULTDIR, "%s-%s-%02d" % (sysInfo['name'], ymd, count))
        if os.path.exists(log):
            count += 1
            continue
        return log


def printLog(logFile, *args):
    fd = open(logFile, 'a', encoding="utf-8")
    if not fd:
        raise RuntimeError(f"can't append to {logFile}")
    if fd.writable():
        fd.write(" ".join(args))
        fd.close()
    else:
        fd.close()
        raise RuntimeError(f"can't write to file {logFile}")


def number(n, what, plural=None):
    plural = what + "s" if not plural else plural
    if not n:
        return f"unknown {plural}"
    else:
        return "%d %s" % (n, what if n == 1 else plural)


def mergeParams(def_, vals):
    params = {}
    for k in def_.keys():
        params[k] = def_[k]
    for k in vals.keys():
        params[k] = vals[k]
    return params


def processCpuFlags(flagStr):
    names = []
    for f in flagStr.split(" "):
        if f in x86CpuFlags:
            names.append(x86CpuFlags[f])
    return ", ".join(names)


def getCpuInfo():
    if sys.platform == "linux":
        cpuinfo = "/proc/cpuinfo"
        kvRegex = re.compile(r'(.+):(.*)')
        cpus = {}
        cpu = 0
        try:
            if os.path.exists(cpuinfo):
                with open(cpuinfo, "r") as fd:
                    line = fd.readline()
                    while line:
                        line = line.strip()
                        if not line:
                            line = fd.readline()
                            continue
                        linePart = kvRegex.findall(line)
                        if len(linePart) < 1:
                            line = fd.readline()
                            continue
                        field = linePart[0][0].strip()
                        value = linePart[0][1].strip()
                        if "processor" in field:
                            cpu = int(value.strip())
                            if cpu not in cpus:
                                cpus[cpu] = {}
                        elif "model name" in field:
                            cpus[cpu]['model'] = value
                        elif "bogomips" in field:
                            cpus[cpu]['bogo'] = float(value)
                        elif "flags" in field:
                            cpus[cpu]['flags'] = processCpuFlags(value)
                        line = fd.readline()
            else:
                raise RuntimeError("cpuinfo not exists")
        except BaseException as e:
            print("cannot read cpuinfo")
            return None
        return cpus
    elif sys.platform == "win32":
        raise NotImplementedError("not supported platform 'win32'")


def getSystemInfo():
    info = {
        'name': getCmdOutput("hostname"),
        'os': getCmdOutput("uname -o"),
        'osRel': getCmdOutput("uname -r"),
        'osVer': getCmdOutput("uname -v"),
        'mach': getCmdOutput("uname -m"),
        'platform': getCmdOutput("uname -i"),
    }
    if not info['os']:
        info['os'] = getCmdOutput("uname -s")

    info['system'] = info['os']
    if os.path.exists("/etc/SuSE-release"):
        info['system'] = getCmdOutput("cat /etc/SuSE-release")
    elif os.path.exists("/etc/release"):
        info['system'] = getCmdOutput("cat /etc/release")

    lang = getCmdOutput("printenv LANG")
    map = getCmdOutput("locale -k LC_CTYPE | grep charmap")
    map = re.sub(r'.*=', '', map)
    coll = getCmdOutput("locale -k LC_COLLATE | grep collate-codeset")
    coll = re.sub(r'.*=', '', coll)
    info['language'] = "%s (charmap=%s, collate=%s)" % (lang, map, coll)

    cpus = getCpuInfo()
    if cpus:
        info['cpus'] = cpus
        info['numCpus'] = len(cpus)

    info['graphics'] = getCmdOutput("3dinfo | cut -f1 -d\'(\'")

    info['runlevel'] = getCmdOutput("runlevel | cut -f2 -d\"(\"")
    info['load'] = getCmdOutput("uptime")
    info['numUsers'] = getCmdOutput("who | wc -l")

    return info


def abortRun(err):
    print("\n" + ("*" * 46), file=sys.stderr)
    print("Run: %s; aborting" % err)
    return sys.exit(1)


def preChecks():
    os.environ['LANG'] = language

    retcode = os.system("make check")
    if retcode:
        retcode = os.system("make all")
        if retcode:
            abortRun("\"make all\" failed")

    with open(os.path.join(TMPDIR, "kill_run"), 'w') as fd:
        fd.write("echo kill -9 %d" % os.getpid())

    os.chmod(os.path.join(TMPDIR, "kill_run"), stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)


def parseArgs():
    arg = argparse.ArgumentParser(description="UnixBench Python-scripted Run")
    arg.add_argument("-q", "--quiet", action="store_true", dest="quiet", default=False, help="quiet mode")
    arg.add_argument("-v", "--verbose", action="store_true", dest="verbose", default=False, help="verbose mode")
    arg.add_argument("-i", "--iterations", dest="iterations", type=str, help="iterations")
    arg.add_argument("-c", "--copies", dest="copies", type=int, nargs="*", help="copies")
    arg.add_argument("test_list", metavar="test list", type=str, nargs="*", help="test items name")

    args = arg.parse_args()
    params = {
        'tests': []
    }
    if args.quiet:
        params['verbose'] = 0
    if args.verbose:
        params['verbose'] = 1
    if args.iterations:
        params['iterations'] = args.iterations
    if args.copies:
        # if 'copies' not in params or not isinstance(params['copies'], list):
        #     params['copies'] = []
        params['copies'] = args.copies
    if args.test_list:
        if 'all' in args.test_list:
            for i, v in testList.items():
                params['tests'].append(v)
        else:
            for i in args.test_list:
                if i not in testList:
                    raise RuntimeError(f"Run: unknown test \"{i}\"")
                if isinstance(testList[i], list):
                    params['tests'].extend(testList[i])
                else:
                    params['tests'].append(testList[i] if testList[i] else i)
            params['tests'] = sorted(list(set(params['tests'])))
    return params


def readResultsFromFile(file):
    if not os.path.exists(file):
        return None

    fd = open(file, "r")
    try:
        results = {}
        line = fd.readline()
        while line:
            line = line.strip()
            if not line:
                line = fd.readline()
                continue
            if line.startswith("#"):
                line = fd.readline()
                continue
            name, time, slab, sum, score, iters = line.split('|')
            bresult = {
                'score': score,
                'scorelabel': slab,
                'time': time,
                'iterations': iters,
            }
            results[name] = bresult
            line = fd.readline()

        fd.close()
        return results
    except BaseException as e:
        if not fd.closed:
            fd.close()
        raise e


def combinePassResults(bench, tdata, bresult, logFile):
    bresult['cat'] = tdata['cat']

    iterations = 0
    totalTime = 0
    sum = 0
    product = 0
    label = None

    pres: dict = bresult['passes']

    npasses = len(pres)
    ndump = npasses // 3

    for presult in sorted(pres, key=lambda x: float(x['COUNT0'])):
        count = float(presult['COUNT0'])
        timebase = int(presult['COUNT1'])
        label = presult['COUNT2']
        time = float(presult['TIME']) if presult['TIME'] else float(presult['elapsed'])

        if ndump > 0:
            printLog(logFile, "*Dump score: %12.1f\n" % count)
            ndump -= 1
            continue

        iterations += 1
        printLog(logFile, "Count score: %12.1f\n" % count)

        if timebase > 0:
            sum += count / (time / timebase)
            product += math.log(count) - math.log(time / timebase)
        else:
            sum += count
            product += math.log(count)
        totalTime += time

    if iterations > 0:
        bresult['score'] = math.exp(product / iterations)
        bresult['scorelabel'] = label
        bresult['time'] = totalTime / iterations
        bresult['iterations'] = iterations
    else:
        bresult['error'] = "No measured results"


def indexResults(results):
    index = readResultsFromFile(os.path.join(BINDIR, "index.base"))
    if not index:
        return

    numCat = {}
    for bench in results['list']:
        bresult = results[bench]
        if bresult['cat'] in numCat:
            numCat[bresult['cat']] += 1
        else:
            numCat[bresult['cat']] = 0
    results['numCat'] = numCat

    numIndex = {}
    indexed = {}
    sum = {}
    for bench in sorted(index.keys()):
        tdata = testParams[bench]
        if not tdata:
            abortRun(f"unknown benchmark \"{bench}\" in {BINDIR}/index.base")

        cat = tdata['cat']
        if cat not in numIndex:
            numIndex[cat] = 0
        numIndex[cat] += 1

        if bench not in results or not results[bench]:
            continue

        iresult = index[bench]
        bresult = results[bench]
        ratio = bresult['score'] / float(iresult['score'])

        bresult['iscore'] = float(iresult['score'])
        bresult['index'] = ratio * 10

        if cat not in sum:
            sum[cat] = 0.0
        sum[cat] += math.log(ratio)
        if cat not in indexed:
            indexed[cat] = 0
        indexed[cat] += 1

    results['indexed'] = indexed
    results['numIndex'] = numIndex
    results['index'] = {}
    for c in sorted(indexed.keys()):
        if indexed[c] > 0:
            results['index'][c] = math.exp(sum[c] / indexed[c]) * 10


def commandBuffered(cmd):
    benchStart = time.time()
    cmdPid, cmdFd = command(cmd)

    cmdFd.wait(300)
    output = cmdFd.stdout.read().decode("utf-8")

    elTime = time.time() - benchStart
    output += ("elapsed|%f\n" % elTime)

    if cmdFd.poll() is not None:
        cmdFd.terminate()
    if not cmdFd.stdin.closed:
        cmdFd.stdin.close()
    if not cmdFd.stdout.closed:
        cmdFd.stdout.close()
    if not cmdFd.stderr.closed:
        cmdFd.stderr.close()
    status = cmdFd.returncode
    output += ("status|%d\n" % status)

    return cmdPid, output


def readResults(pid, output):
    presult = {
        'pid': pid,
        'ERROR': "",
    }
    for line in output.split('\n'):
        line: str = line.strip()
        splitParams = line.split('|')
        field = splitParams[0]
        if len(splitParams) <= 1:
            presult['ERROR'] += ("\n" if presult['ERROR'] else "")
            presult['ERROR'] += field
        elif len(splitParams) == 2:
            presult[field] = splitParams[1]
        else:
            # Store the values in separate fields, named "FIELD{i}".
            for x in range(len(splitParams) -1):
                presult[f"{field}{x}"] = splitParams[x + 1]

    if presult['status'] != 0 and ('ERROR' not in presult):
        presult['ERROR'] = f"command returned status {presult['status']}"

    return presult


def executeBenchmark(command, copies):
    ctxt = []

    for i in range(copies):
        cmdPid, cmdOutput = commandBuffered(command)
        ctxt.append({
            'pid': cmdPid,
            'fd': cmdOutput
        })

    pres = []
    for i in range(copies):
        presult = readResults(ctxt[i]['pid'], ctxt[i]['fd'])
        pres.append(presult)

    return pres


def runOnePass(params, verbose, logFile, copies):
    command = params['command']
    if verbose > 1:
        print()
        print(f"COMMAND: \"{command}\"")
        print(f"COPIES: \"{copies}\"")

    pwd = os.getcwd()
    os.chdir(TESTDIR)

    copyResults = executeBenchmark(command, copies)
    printLog(logFile, "\n")

    os.chdir(pwd)

    count = time = elap = 0

    for res in copyResults:
        for k in sorted(res.keys()):
            printLog(logFile, f"# {k}: {res[k]}\n")
        printLog(logFile, "\n")

        if 'ERROR' in res and res['ERROR']:
            name = params['logmsg']
            abortRun(f"\"{name}\": {res['ERROR']}")

        count += float(res['COUNT0'])
        time += float(res['TIME']) if 'TIME' in res and res['TIME'] else float(res['elapsed'])
        elap += float(res['elapsed'])

    passResult = copyResults[0]
    passResult['COUNT0'] = count
    passResult['TIME'] = time / copies
    passResult['elapsed'] = elap / copies

    return passResult


def runBenchmark(bench, tparams, verbose, logFile, copies):
    params = mergeParams(baseParams, tparams)

    prog = params['prog'] if 'prog' in params and params['prog'] else os.path.join(BINDIR, bench)
    command = "\"%s\" %s" % (prog, params['options'])
    command += f" < \"{params['stdin']}\"" if params['stdin'] else ""
    command += " 2>&1"
    command += f" >> \"{logFile}\"" if params['stdout'] else " > /dev/null"
    params['command'] = command

    bresult = {
        'name': bench,
        'msg': params['logmsg']
    }

    if verbose > 0:
        print("\n%d x %s " % (copies, params['logmsg']), end="")

    printLog(logFile, "\n########################################################")
    printLog(logFile, "%s -- %s" % (params['logmsg'], number(copies, "copy", "copies")))
    printLog(logFile, "==> %s\n\n" % command)

    repeats = longIterCount if params['repeat'] == 'long' else shortIterCount
    repeats = 1 if params['repeat'] == "single" else repeats
    pres = []
    for i in range(1, repeats + 1):
        printLog(logFile, "#### Pass %d\n\n" % i)

        if sys.platform == 'linux':
            os.sync()
            time.sleep(1)
            os.sync()
            time.sleep(2)

        if verbose > 0:
            print(" %d" % i, end="", flush=True)

        presult = runOnePass(params, verbose, logFile, copies)
        pres.append(presult)

    bresult['passes'] = pres

    combinePassResults(bench, tparams, bresult, logFile)

    if copies == 1:
        printLog(logFile, "\n>>>> Result of 1 copy\n")
    else:
        printLog(logFile, "\n>>>> Sum of %d copies\n" % copies)

    for k in ('score', 'time', 'iterations'):
        printLog(logFile, ">>>> %s: %s\n" % (k, bresult[k]))

    printLog(logFile, "\n")

    if bench == "C":
        os.unlink(os.path.join(TESTDIR, "cctest.o"))
        os.unlink(os.path.join(TESTDIR, "a.out"))
    if verbose > 0:
        print("\n")

    return bresult


def runTests(tests, verbose, logFile, copies):
    results = {
        'start': time.time(),
        'copies': copies
    }
    for bench in tests:
        if bench not in testParams:
            abortRun(f"unknown benchmark \"{bench}\"")
        params = testParams[bench]

        cat = params['cat']
        maxCopies = testCats[cat]['maxCopies']
        if copies > maxCopies:
            continue

        bresult = runBenchmark(bench, params, verbose, logFile, copies)
        results[bench] = bresult
    results['end'] = time.time()

    benches = filter(lambda key: key in results and isinstance(results[key], dict) and "msg" in results[key]['msg'],
                     results.keys())
    benches = sorted(benches, key=lambda x: x['msg'])
    results['list'] = benches

    indexResults(results)
    return results


def displaySystem(info, fd):
    print("   System %s: %s" % (info['name'], info['system']), file=fd)
    print("   OS: %s -- %s -- %s" % (info['os'], info['osRel'], info['osVer']), file=fd)
    print("   Machine: %s (%s)" % (info['mach'], info['platform']), file=fd)
    print("   Language: %s" % info['language'], file=fd)

    if "cpus" not in info:
        print("   CPU: no details avaliable", file=fd)
    else:
        cpus = info['cpus']

        for i, v in cpus.items():
            print("   CPU %d: %s (%.1f bogomips)" % (i, v['model'], v['bogo']), file=fd)
            print("          %s" % cpus[i]['flags'], file=fd)

    if 'graphics' in info and info['graphics']:
        print("  Graphics: %s", info['graphics'], file=fd)

    print("   %s; runlevel %s\n" % (info['load'], info['runlevel']), file=fd)


def logResults(results, outFd):
    for bench in results['list']:
        bresult = results[bench]

        print("%-40s %12.1f %-5s (%.1f s, %d samples)" % (
            bresult['msg'],
            bresult['score'],
            bresult['scorelabel'],
            bresult['time'],
            bresult['iterations']
        ), file=outFd)

        print(file=outFd)


def logIndexCat(results, cat, outFd):
    total = results['numIndex'][cat] if 'numIndex' in results and cat in results['numIndex'] else None
    indexed = results['indexed'][cat] if 'indexed' in results and cat in results['indexed'] else None
    iscore = results['index'][cat] if 'index' in results and cat in results['index'] else None
    full = bool(total == indexed)

    if indexed is None or indexed == 0:
        print("No index results avaliable for %s\n" % testCats[cat]['name'], file=outFd)
        return

    head = testCats[cat]['name'] + (" Index Values" if full else " Partial Index")
    print("%-40s %12s %12s %8s" % (head, "BASELINE", "RESULT", "INDEX"), file=outFd)

    for bench in results['list']:
        bresult = results[bench]
        if bresult['cat'] != cat:
            continue

        if 'iscore' in bresult and 'index' in bresult:
            print("%-40s %12.1f %12.1f %8.1f" % (
                bresult['msg'], bresult['iscore'],
                bresult['score'], bresult['index']
            ), file=outFd)
        else:
            print("%-40s %12s %12.1f %8s" % (
                bresult['msg'], "---",
                bresult['score'], "---"
            ), file=outFd)

    title = testCats[cat]['name'] + " Index Score"
    if not full:
        title += " (Partial Only)"
    print("%-40s %12s %12s %8s" % ("", "", "", "========"), file=outFd)
    print("%-66s %8.1f" % (title, iscore), file=outFd)

    print(file=outFd)


def logIndex(results, outFd):
    count = results['indexed']
    for cat in count.keys():
        logIndexCat(results, cat, outFd)


def summarizeRun(systemInfo, results, verbose, reportFd):
    print("------------------------------------------------------------------------", file=reportFd)
    print("Benchmark Run: %s %s - %s" % (
        time.strftime("%Y-%m-%d", time.localtime(results['start'])),
        time.strftime("%H:%M:%S", time.localtime(results['start'])),
        time.strftime("%H:%M:%S", time.localtime(results['end']))
    ), file=reportFd)
    print("%s in system; running %s of tests" % (
        number(systemInfo['numCpus'], "CPU"),
        number(results['copies'], "parallel copy", "parallel copies")
    ), file=reportFd)
    print(file=reportFd)

    logResults(results, reportFd)

    logIndex(results, reportFd)


def runHeaderHtml(systemInfo, reportFd):
    title = "Benchmark of %s / %s on %s" % (
        systemInfo['name'], systemInfo['system'],
        time.strftime("%Y-%m-%d", time.localtime())
    )
    print("""
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
"http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <meta name="keywords" content="linux, benchmarks, benchmarking">
  <title>$title</title>
  <style type="text/css">
    table {
      margin: 1em 1em 1em 0;
      background: #f9f9f9;
      border: 1px #aaaaaa solid;
      border-collapse: collapse;
    }

    table th, table td {
      border: 1px #aaaaaa solid;
      padding: 0.2em;
    }

    table th {
      background: #f2f2f2;
      text-align: center;
    }
  </style>
</head>
<body>""", file=reportFd)

    print("<h2>%s</h2>" % title, file=reportFd)
    print("<p><b>BYTE UNIX Benchmarks (Version %s)</b></p>\n" % version, file=reportFd)


def displaySystemHtml(info, fd):
    print("<h3>Test System Information</h3>", file=fd)
    print("<p><table>", file=fd)

    print("<tr>", file=fd)
    print("    <td><b>System:</b></td>", file=fd)
    print("    <td colspan=2>%s: %s</td>" % (info['name'], info['system']), file=fd)
    print("</tr><tr>", file=fd)
    print("    <td><b>OS:</b></td>", file=fd)
    print("    <td colspan=2>%s -- %s -- %s</td>" % (info['os'], info['osRel'], info['osVer']), file=fd)
    print("</tr><tr>", file=fd)
    print("    <td><b>Machine:</b></td>", file=fd)
    print("    <td colspan=2>%s: %s</td>" % (info['mach'], info['platform']), file=fd)
    print("</tr><tr>", file=fd)
    print("    <td><b>Language:</b></td>", file=fd)
    print("    <td colspan=2>%s</td>" % info['language'], file=fd)
    print("</tr>", file=fd)

    if 'cpus' not in info:
        print("<tr>", file=fd)
        print("    <td><b>CPUs:</b></td>", file=fd)
        print("    <td colspan=2>no details available</td>", file=fd)
        print("</tr>", file=fd)
    else:
        cpus = info['cpus']
        for i, v in enumerate(cpus):
            print("<tr>", file=fd)
            if i == 0:
                print("    <td rowspan=%d><b>CPUs:</b></td>" % (i + 1), file=fd)
            print("    <td><b>%d:</b></td>" % i, file=fd)
            print("    <td>%s (%.1f bogomips)<br />" % (cpus[i]['model'], cpus[i]['bogo']), file=fd)
            print("    %s</td>" % cpus[i]['flags'], file=fd)
            print("</tr>", file=fd)

    if "graphics" in info and info['graphics']:
        print("<tr>", file=fd)
        print("    <td><b>Graphics:</b></td>", file=fd)
        print("    <td colspan=2>%s</td>" % info['graphics'], file=fd)
        print("</tr>", file=fd)

    print("<tr>", file=fd)
    print("    <td><b>Uptime:</b></td>", file=fd)
    print("    <td colspan=2>%s; runlevel %s</td>" % (info['load'], info['runlevel']), file=fd)
    print("</tr>", file=fd)

    print("</table></p>\n", file=fd)


def logCatResultHtml(results, cat, fd):
    numIndex = results['numIndex'][cat] if 'numIndex' in results and cat in results['numIndex'] else None
    indexed = results['indexed'][cat] if 'indexed' in results and cat in results['indexed'] else None
    iscore = results['index'][cat] if "index" in results and cat in results['index'] else None
    full = indexed is not None and indexed == numIndex

    if "numCat" not in results or cat not in results['numCat'] or results['numCat'][cat] == 0:
        return

    warn = ""
    if indexed and indexed == 0:
        warn = " - no index results available"
    elif not full:
        warn = " - not all index tests were run;" + \
               " only a partial index score is available"
    print("<h4>%s%s</h4>" % (testCats[cat]['name'], warn), file=fd)

    print("<p><table width=\"100%\"", file=fd)

    print("<tr>", file=fd)
    print("    <th align=left>Test</th>", file=fd)
    print("    <th align=right>Score</th>", file=fd)
    print("    <th align=left>Unit</th>", file=fd)
    print("    <th align=right>Time</th>", file=fd)
    print("    <th align=right>Iters.</th>", file=fd)
    print("    <th align=right>Baseline</th>", file=fd)
    print("    <th align=right>Index</th>", file=fd)
    print("</tr>", file=fd)

    for bench in results['list']:
        bresult = results[bench]
        if bresult['cat'] != cat:
            continue

        print("<tr>", file=fd)
        print("    <td><b>%s</b></td>" % bresult['msg'], file=fd)
        print("    <td align=right><tt>%.1f</tt></td>" % bresult['score'], file=fd)
        print("    <td align=left><tt>%s</tt></td>" % bresult['scorelabel'], file=fd)
        print("    <td align=right><tt>%.1f s</tt></td>" % bresult['time'], file=fd)
        print("    <td align=right><tt>%d</tt></td>" % bresult['iterations'], file=fd)

        if "index" in bresult and bresult['index']:
            print("    <td align=right><tt>%.1f</tt></td>" % bresult['iscore'], file=fd)
            print("    <td align=right><tt>%.1f</tt></td>" % bresult['index'], file=fd)

        print("</tr>", file=fd)

    if indexed and indexed > 0:
        title = testCats[cat]['name'] + " Index Score"
        if not full:
            title += " (Partial Only)"
        print("<tr>", file=fd)
        print("    <td colspan=6><b>%s:</b></td>" % title, file=fd)
        print("    <td align=right><b><tt>%.1f</tt></b></td>" % iscore, file=fd)
        print("</tr>", file=fd)

    print("</table></p>\n", file=fd)


def logResultsHtml(results, fd):
    for cat in testCats.keys():
        logCatResultHtml(results, cat, fd)


def summarizeRunHtml(systemInfo, results, verbose, reportFd):
    time_ = results['end'] - results['start']
    print("<p><hr/></p>", file=reportFd)
    print("<h3>Benchmark Run: %s; %s</h3>" % (
        number(systemInfo['numCpus'], "CPU"),
        number(results['copies'], "parallel process", "parallel processes")
    ), file=reportFd)
    print("<p>Time: %s - %s; %dm %02ds</p>" % (
        time.strftime("%H:%M:%S", time.localtime(results['start'])),
        time.strftime("%H:%M:%S", time.localtime(results['end'])),
        int(time_ // 60), time_ % 60
    ), file=reportFd)
    print(file=reportFd)

    logResultsHtml(results, reportFd)


def runFooterHtml(reportFd):
    print("""
<p><hr/></p>
<div><b>No Warranties:</b> This information is provided free of charge and "as
is" without any warranty, condition, or representation of any kind,
either express or implied, including but not limited to, any warranty
respecting non-infringement, and the implied warranties of conditions
of merchantability and fitness for a particular purpose. All logos or
trademarks on this site are the property of their respective owner. In
no event shall the author be liable for any
direct, indirect, special, incidental, consequential or other damages
howsoever caused whether arising in contract, tort, or otherwise,
arising out of or in connection with the use or performance of the
information contained on this web site.</div>
</body>
</html>""", file=reportFd)


# MAIN

def main():
    params = parseArgs()
    verbose = params['verbose'] if 'verbose' in params and params['verbose'] else 1
    if 'iterations' in params and params['iterations']:
        longIterCount = params['iterations']
        shortIterCount = int((params['iterations'] + 1) // 3)
        shortIterCount = 1 if shortIterCount < 1 else shortIterCount

    tests = params['tests'] if 'tests' in params else {}
    if len(tests) <= 0:
        tests = index

    preChecks()
    systemInfo = getSystemInfo()

    copies = params['copies'] if 'copies' in params else []
    if not copies or len(copies) == 0:
        copies.append(1)
        if 'numCpus' in systemInfo and systemInfo['numCpus'] > 1:
            copies.append(systemInfo['numCpus'])

    os.system(f"cat \"{os.path.join(BINDIR, 'unixbench.logo')}\"")

    if verbose > 1:
        print(f"\n{tests.join(', ')}", end="")
        print("Tests to run: %s" % tests.join(", "))

    reportFile = logFile_(systemInfo)
    reportHtml = reportFile + ".html"
    logFile = reportFile + ".log"

    reportFd = reportFd2 = None
    try:
        #reportFd = open(reportFile, "w", encoding="utf-8")
        reportFd = sys.stdout
        reportFd2 = open(reportHtml, "w", encoding="utf-8")

        print("   BYTE UNIX Benchmarks (Version %s)\n" % version, file=reportFd)
        runHeaderHtml(systemInfo, reportFd2)

        displaySystem(systemInfo, reportFd)
        displaySystemHtml(systemInfo, reportFd2)

        for c in copies:
            if verbose > 1:
                print("Run with %s", number(c, "copy", "copies"))
            results = runTests(tests, verbose, logFile, c)

            summarizeRun(systemInfo, results, verbose, reportFd)
            summarizeRunHtml(systemInfo, results, verbose, reportFd2)

        runFooterHtml(reportFd2)

        if verbose > 0:
            print()
            print("========================================================================")
            os.system(f"cat \"{reportFile}\"")

    finally:
        if reportFd and not reportFd.closed:
            reportFd.close()
        if reportFd2 and not reportFd2.closed:
            reportFd2.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
