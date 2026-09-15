"""Small SVG explanation with exact spherical-slab fractions, not dose errors."""
from pathlib import Path
from math import pi, sqrt
from html import escape


def main():
    r=(3*6.5/(4*pi))**(1/3)
    def fraction(radius,h=1):
        return 100*(3*h/(4*radius)-h**3/(16*radius**3))
    small,large=fraction(r),fraction(10)
    assert 60<small<62 and 7.4<large<7.6
    svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 440" role="img" aria-label="Coarse versus fine sampling, and geometric sensitivity of small targets">',
         '<rect width="1080" height="440" fill="white"/>']
    def text(x,y,value,size=16,fill='#243d4b',anchor='start',bold=False):
        svg.append(f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{700 if bold else 400}">{escape(value)}</text>')
    text(25,31,'Why small targets need volume-aware dose evaluation',23,bold=True)
    for x,title in [(25,'A  Coarse plane-only readout'),(382,'B  Fine volume sampling'),(740,'C  Same 1-mm slab')]:
        text(x,72,title,18,bold=True)
    scale=70
    for cx in [175,532]:
        svg.append(f'<circle cx="{cx}" cy="202" r="{r*scale:.2f}" fill="#e6f5f4" stroke="#12808a" stroke-width="2.5"/>')
    for z in [-1.5,-.5,.5,1.5]:
        y=202-z*scale
        svg.append(f'<path d="M55 {y} H295" stroke="#c36a20" stroke-width="1.5" stroke-dasharray="5 4"/>')
        if abs(z)<r:
            extent=sqrt(r*r-z*z)*scale
            svg.append(f'<path d="M{175-extent:.2f} {y} H{175+extent:.2f}" stroke="#c36a20" stroke-width="4"/>')
    text(175,333,'Few cross-sections carry most',15,anchor='middle')
    text(175,354,'of the small target’s weight.',15,anchor='middle')
    for a in range(-5,6):
        for b in range(-5,6):
            x,z=a*.2,b*.2
            if x*x+z*z<r*r:
                svg.append(f'<circle cx="{532+x*scale:.1f}" cy="{202-z*scale:.1f}" r="2.2" fill="#12808a"/>')
    text(532,333,'Sample through the represented',15,anchor='middle')
    text(532,354,'volume, then check refinement.',15,anchor='middle')
    for y,label,value in [(142,'2.32-mm sphere · 6.5 mm³',small),(239,'20-mm sphere · 4,189 mm³',large)]:
        text(740,y,label,15,bold=True)
        svg.append(f'<rect x="740" y="{y+15}" width="290" height="25" fill="#edf1f4" rx="3"/>')
        svg.append(f'<rect x="740" y="{y+15}" width="{2.9*value:.2f}" height="25" fill="#12808a" rx="3"/>')
        text(740,y+63,f'{value:.1f}% of total volume',16)
    text(740,354,'Geometric fraction, not DVH error.',14,fill='#536977')
    text(25,397,'A/B: schematic sections of the same 2.32-mm sphere; A planes are 1 mm apart.',14,fill='#536977')
    text(25,420,'A small target needs dose samples throughout its volume, including between the CT planes.',15,fill='#536977')
    svg.append('</svg>')
    path=Path(__file__).resolve().parents[1]/'docs/sampling_explained.svg'
    path.write_text('\n'.join(svg),encoding='utf-8')
    print(f'{path.name}: {path.stat().st_size} bytes; central slab {small:.3f}% / {large:.3f}%')


if __name__=='__main__':main()
