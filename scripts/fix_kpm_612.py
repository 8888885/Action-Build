#!/usr/bin/env python3
"""
Fix KPM for Kernel 6.12
This script patches SukiSU Ultra's KPM code to work with kernel 6.12
"""

import sys
import os

def fix_super_access():
    """Fix super_access.c - remove cb_mutex for kernel 6.1+"""
    filepath = 'kernel/kpm/super_access.c'
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} (file not found)")
        return
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    with open(filepath, 'w') as f:
        for line in lines:
            if 'DEFINE_MEMBER(netlink_kernel_cfg, cb_mutex)' not in line:
                f.write(line)
    
    print(f"Fixed {filepath}: removed cb_mutex line")

def fix_lsm_hook():
    """Fix lsm_hook.c - fix security_add_hooks signature for 6.8+"""
    filepath = 'kernel/hook/lsm_hook.c'
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} (file not found)")
        return
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    old = 'security_add_hooks(ksu_hooks, ARRAY_SIZE(ksu_hooks), "ksu");'
    new = '''#if LINUX_VERSION_CODE >= KERNEL_VERSION(6, 8, 0)
    static struct lsm_id ksu_lsm_id = { .name = "ksu", .id = LSM_ID_EXT };
    security_add_hooks(ksu_hooks, ARRAY_SIZE(ksu_hooks), &ksu_lsm_id);
#else
    security_add_hooks(ksu_hooks, ARRAY_SIZE(ksu_hooks), "ksu");
#endif'''
    
    if old in content:
        content = content.replace(old, new)
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Fixed {filepath}")
    else:
        print(f"Pattern not found in {filepath}")
    
    # Add include for lsm_id if needed
    if 'LSM_ID_EXT' in content and '#include <linux/lsm_hooks.h>' not in content:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        with open(filepath, 'w') as f:
            f.write('#include <linux/lsm_hooks.h>\n')
            f.writelines(lines)
        print(f"Added lsm_hooks.h include to {filepath}")

def main():
    print("=== Fixing KPM for Kernel 6.12 ===")
    fix_super_access()
    fix_lsm_hook()
    print("=== KPM 6.12 fixes applied ===")

if __name__ == '__main__':
    main()
