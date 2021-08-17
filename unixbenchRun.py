#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##############################################################
# UnixBench - Release 5.1.3, based on:
# The BYTE UNIX Benchmarks - Release 3
#  Module: Run   SID: 3.11 5/15/91 19:30:14
# Original Byte benchmarks written by:
# Ruilx Alxa  GT-Soft Studio
#
##############################################################
# Replacing UnixBench Perl Script
##############################################################

import os, sys, time, datetime

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

import subprocess
# Utilities

def command(cmd):
	process = subprocess.Popen(cmd,
							   bufsize=0,
							   stdin=subprocess.PIPE,
							   stdout=subprocess.PIPE,
							   stderr=subprocess.PIPE,
							   shell=True,
							   encoding="utf-8")
	pid = process.pid
	return pid, process

def getCmdOutput(cmd):
	timeout = 10
	pid, process = command(cmd)
	returnCode = process.wait(timeout)
	if not process.poll():
		process.terminate()
		raise RuntimeError(f"Process '{process.pid}' ran timeout({timeout}s)")
	stdout = process.stdout.read()
	return stdout

def logFile(sysInfo):
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
		raise RuntimeError(f"can't write to file {logfile}")

def number(n, what, plural):
	plural = what + "s" if not plural
	if n:
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
	...

