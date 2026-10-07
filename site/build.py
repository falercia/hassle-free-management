"""Regenera os dados e as miniaturas do site a partir da pasta posts/.

Uso, na raiz do repositorio:  python3 site/build.py
Requer Pillow (pip install pillow).
"""
import glob, json, os, re
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(ROOT, 'posts')
SITE = os.path.join(ROOT, 'site')
THUMBS = os.path.join(SITE, 'thumbs')
THUMB_W, THUMB_H = 600, 750
FEATURED = '01'  # tema usado na faixa 'Um tema, dez paginas' do site
ANATOMY = os.path.join(SITE, 'anatomy')

TERRITORIES = {
    1: ['Pessoas e Liderança', 'People and Leadership'],
    2: ['Performance, Metas e Métricas', 'Performance, Goals and Metrics'],
    3: ['Execução e Processos', 'Execution and Process'],
    4: ['Cultura e Comportamento', 'Culture and Behavior'],
    5: ['Comunicação e Influência', 'Communication and Influence'],
    6: ['Tempo e Foco do Líder', "The Leader's Time and Focus"],
    7: ['Times, Estrutura e Crescimento', 'Teams, Structure and Growth'],
}


def first_paragraph(text, header):
    i = text.find(header)
    return text[i + len(header):].strip().split('\n\n')[0].strip() if i >= 0 else ''


def field(pattern, text):
    m = re.search(pattern, text)
    return m.group(1).strip() if m else ''


def thumb(src, dst, size=(THUMB_W, THUMB_H)):
    if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
        return
    im = Image.open(src).convert('RGB')
    im = im.resize(size, Image.LANCZOS)
    im.save(dst, 'JPEG', quality=80, optimize=True, progressive=True)


def main():
    os.makedirs(THUMBS, exist_ok=True)
    rows = []
    for d in sorted(os.listdir(POSTS)):
        p = os.path.join(POSTS, d)
        if not (os.path.isdir(p) and d[:2].isdigit()):
            continue
        pt = open(os.path.join(p, 'legenda.md'), encoding='utf-8').read()
        en = open(os.path.join(p, 'caption-en.md'), encoding='utf-8').read()
        n = d[:2]
        rows.append({
            'n': n,
            'dir': d,
            'title': [pt.splitlines()[0].split('·')[-1].strip(), en.splitlines()[0].split('·')[-1].strip()],
            'territory': int(field(r'\*\*Pilar:\*\*\s*(\d+)', pt) or 0),
            'hook': [first_paragraph(pt, '## Legenda sugerida para o LinkedIn'),
                     first_paragraph(en, '## Suggested LinkedIn caption')],
            'about': [field(r'\*\*Neste post:\*\*\s*(.+)', pt), field(r'\*\*In this post:\*\*\s*(.+)', en)],
            'pdf': [os.path.basename(glob.glob(os.path.join(p, 'GSC-*.pdf'))[0]),
                    os.path.basename(glob.glob(os.path.join(p, 'EN-GSC-*.pdf'))[0])],
        })
        thumb(os.path.join(p, 'slides', 'slide-01.png'), os.path.join(THUMBS, f'{n}-pt.jpg'))
        thumb(os.path.join(p, 'slides-en', 'slide-01.png'), os.path.join(THUMBS, f'{n}-en.jpg'))
        if n == FEATURED:
            os.makedirs(ANATOMY, exist_ok=True)
            for i in range(1, 11):
                for folder, lang in (('slides', 'pt'), ('slides-en', 'en')):
                    thumb(os.path.join(p, folder, f'slide-{i:02d}.png'),
                          os.path.join(ANATOMY, f'{lang}-{i:02d}.jpg'), (360, 450))
    with open(os.path.join(SITE, 'posts.js'), 'w', encoding='utf-8') as f:
        f.write('// Gerado por site/build.py, nao editar a mao.\n')
        f.write('window.TERRITORIES = ' + json.dumps(TERRITORIES, ensure_ascii=False) + ';\n')
        f.write('window.POSTS = ' + json.dumps(rows, ensure_ascii=False, indent=1) + ';\n')
    print(f'{len(rows)} posts, miniaturas em site/thumbs/')


if __name__ == '__main__':
    main()
