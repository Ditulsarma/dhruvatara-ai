import re,os
root = r'c:\Users\DitulSarma\Astrology\AiDhrubatara\my-web-app'
exts = {'.py','.html','.htm','.txt','.json','.md','.js','.css'}
pattern = re.compile(r"\s*\]*\]")
total_removed=0
files_changed=0
for dirpath,dirs,files in os.walk(root):
    if 'venv' in dirpath.split(os.sep):
        continue
    for fname in files:
        _,ext = os.path.splitext(fname)
        if ext.lower() in exts:
            path = os.path.join(dirpath,fname)
            try:
                with open(path,'r',encoding='utf-8') as f:
                    s = f.read()
            except Exception:
                continue
            matches = pattern.findall(s)
            if matches:
                new = pattern.sub('', s)
                with open(path,'w',encoding='utf-8') as f:
                    f.write(new)
                print(f'Cleaned {len(matches)} in {path}')
                total_removed += len(matches)
                files_changed += 1
print(f'Total removed: {total_removed} across {files_changed} files')
