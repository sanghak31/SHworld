import streamlit as st

st.set_page_config(
    page_title="생명과학 시뮬레이션 실험실",
    page_icon="🧬",
    layout="wide",
)

# ──────────────────────────────────────────────
# 시뮬레이션 목록 — 새 앱을 추가하려면 여기에 항목만 넣으면 됩니다.
# ──────────────────────────────────────────────
SECTIONS = [
    {
        "title": "유전과 진화",
        "desc": "염기서열에서 개체군의 변화까지",
        "apps": [
            {
                "name": "DNA 염기서열 변환기 🧬",
                "desc": "DNA 염기서열을 입력해 변환하고 분석해 봅니다.",
                "url": "https://geneticanalysis.streamlit.app/",
                "color": "#1f8a70",
            },
            {
                "name": "자연선택 🦎",
                "desc": "환경 조건에 따라 개체군이 어떻게 달라지는지 관찰합니다.",
                "url": "https://naturalselection.streamlit.app/",
                "color": "#d9822b",
            },
        ],
    },
    {
        "title": "항상성과 방어",
        "desc": "몸속 조절 작용과 면역 반응",
        "apps": [
            {
                "name": "면역 반응 시뮬레이션 🛡️",
                "desc": "백신 접종 이후 면역 반응이 진행되는 과정을 살펴봅니다.",
                "url": "https://shvaccinesimulation.streamlit.app/",
                "color": "#3b6fb6",
            },
            {
                "name": "ADH 시뮬레이션 💧",
                "desc": "항이뇨 호르몬(ADH)에 따른 체내 수분 조절을 확인합니다.",
                "url": "https://adhsimulation.streamlit.app/",
                "color": "#8a5db3",
            },
            {
                "name": "TI 시뮬레이션 🧪",
                "desc": "변수를 조절하며 결과가 어떻게 바뀌는지 실험해 봅니다.",
                "url": "https://tisimulation.streamlit.app/",
                "color": "#2f9aa8",
            },
        ],
    },
    {
        "title": "신경",
        "desc": "자극이 전달되는 과정",
        "apps": [
            {
                "name": "뉴런 흥분 전도 ⚡",
                "desc": "뉴런에서 흥분이 전도되는 과정을 단계별로 확인합니다.",
                "url": "https://neuronconduction.streamlit.app/",
                "color": "#c4475a",
            },
        ],
    },
    {
        "title": "세포와 실험",
        "desc": "세포소기관을 분리하는 실험 기법",
        "apps": [
            {
                "name": "세포 분획법 실험실 🧫",
                "desc": "균질화한 세포액을 원심분리해 세포소기관을 분리하고 분석해 봅니다.",
                "url": "https://fractionation.streamlit.app/",
                "color": "#6a9a3a",
            },
        ],
    },
]

# ──────────────────────────────────────────────
# 스타일 (테마 색은 상속하므로 라이트/다크 모두 자연스럽게 맞춰집니다)
# ──────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@700;900&display=swap');
.block-container{max-width:1080px;padding-top:2.5rem;}
header[data-testid="stHeader"]{background:transparent;}
.hero-title{font-family:'Noto Serif KR',serif !important;font-weight:900 !important;
  font-size:clamp(1.4rem,3vw,2.4rem) !important;line-height:1.35 !important;letter-spacing:-.02em;
  margin:0 0 .8rem !important;padding:0 !important;word-break:keep-all;}
.hero-lead{opacity:.75;font-size:1.05rem;line-height:1.7;margin:0;max-width:34em;}
.sec-title{font-family:'Noto Serif KR',serif;font-weight:700;font-size:1.35rem;margin:1.8rem 0 .1rem;}
.sec-desc{opacity:.7;font-size:.95rem;margin:0 0 .9rem;}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px;}
a.card{display:flex;flex-direction:column;gap:6px;text-decoration:none !important;color:inherit !important;
  background:rgba(128,128,128,.08);border:1px solid rgba(128,128,128,.28);
  border-top:6px solid var(--c);border-radius:14px;padding:18px 18px 16px;
  transition:transform .18s,border-color .18s;}
a.card:hover{transform:translateY(-3px);border-color:var(--c);}
a.card:focus-visible{outline:3px solid var(--c);outline-offset:3px;}
a.card h3{margin:0;padding:0;font-size:1.12rem;color:inherit;}
a.card p{margin:0;opacity:.75;font-size:.93rem;line-height:1.6;flex:1;}
a.card .go{color:var(--c);font-weight:600;font-size:.92rem;margin-top:6px;}
.site-footer{border-top:1px solid rgba(128,128,128,.28);margin-top:2rem;padding:1.1rem 0 .5rem;
  text-align:center;opacity:.7;font-size:.9rem;}
.note{border-left:4px solid #d9822b;padding:.3rem .9rem;opacity:.75;font-size:.9rem;margin:2rem 0 1rem;}
@media (prefers-reduced-motion:reduce){a.card{transition:none;}}
</style>
""",
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────
# 히어로: 제목 + 회전하는 DNA 이중나선
# ──────────────────────────────────────────────
HELIX_HTML = """
<svg id="helix" viewBox="0 0 320 340" width="100%" height="320"
     role="img" aria-label="천천히 회전하는 DNA 이중나선"></svg>
<script>
(function(){
  var svg=document.getElementById('helix'),NS='http://www.w3.org/2000/svg',N=15,
      cols=['#1f8a70','#d9822b','#3b6fb6','#c4475a'],rungs=[],a=[],b=[];
  for(var i=0;i<N;i++){
    var r=document.createElementNS(NS,'line');
    r.setAttribute('stroke-width','4');r.setAttribute('stroke-linecap','round');
    svg.appendChild(r);rungs.push(r);
  }
  for(var i=0;i<N;i++){
    var p=document.createElementNS(NS,'circle'),q=document.createElementNS(NS,'circle');
    p.setAttribute('fill',cols[i%4]);q.setAttribute('fill',cols[(i+2)%4]);
    svg.appendChild(p);svg.appendChild(q);a.push(p);b.push(q);
  }
  function draw(t){
    for(var i=0;i<N;i++){
      var y=24+i*21.5,ph=t+i*0.55,x1=160+Math.sin(ph)*90,x2=160-Math.sin(ph)*90,d=Math.cos(ph);
      rungs[i].setAttribute('x1',x1);rungs[i].setAttribute('x2',x2);
      rungs[i].setAttribute('y1',y);rungs[i].setAttribute('y2',y);
      rungs[i].setAttribute('stroke',cols[i%4]);rungs[i].setAttribute('opacity','.45');
      a[i].setAttribute('cx',x1);a[i].setAttribute('cy',y);
      a[i].setAttribute('r',8+d*3);a[i].setAttribute('opacity',.65+d*.35);
      b[i].setAttribute('cx',x2);b[i].setAttribute('cy',y);
      b[i].setAttribute('r',8-d*3);b[i].setAttribute('opacity',.65-d*.35);
    }
  }
  draw(0);
  if(!window.matchMedia('(prefers-reduced-motion: reduce)').matches){
    var s=null;(function f(ts){if(s===null)s=ts;draw((ts-s)/1400);requestAnimationFrame(f)})(0);
  }
})();
</script>
"""

def render_html(html, height):
    """최신 Streamlit은 st.iframe, 이전 버전은 components.html을 사용합니다."""
    if hasattr(st, "iframe"):
        st.iframe(html.strip(), height=height)
    else:
        import streamlit.components.v1 as components
        components.html(html, height=height)


left, right = st.columns([1.25, 0.75], vertical_alignment="center")
with left:
    st.markdown(
        '<h1 class="hero-title">눈에 보이지 않는 생명 현상을,<br>직접 움직여 보세요</h1>'
        '<p class="hero-lead">유전, 진화, 면역, 신경까지. 변수를 바꾸면 결과가 바로 달라지는 '
        "생명과학 시뮬레이션 모음입니다.</p>",
        unsafe_allow_html=True,
    )
with right:
    render_html(HELIX_HTML, height=330)

# ──────────────────────────────────────────────
# 시뮬레이션 카드
# ──────────────────────────────────────────────
def card_html(app: dict) -> str:
    return (
        f'<a class="card" style="--c:{app["color"]}" href="{app["url"]}" '
        f'target="_blank" rel="noopener">'
        f'<h3>{app["name"]}</h3><p>{app["desc"]}</p><span class="go">열기 →</span></a>'
    )


for section in SECTIONS:
    cards = "".join(card_html(a) for a in section["apps"])
    st.markdown(
        f'<div class="sec-title">{section["title"]}</div>'
        f'<div class="sec-desc">{section["desc"]}</div>'
        f'<div class="grid">{cards}</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="note">시뮬레이션은 Streamlit 무료 서버에서 실행됩니다. '
    "한동안 접속이 없었다면 처음 열 때 깨우는 데 잠시 걸릴 수 있어요.</div>",
    unsafe_allow_html=True,
)

st.markdown('<div class="site-footer">by LSH</div>', unsafe_allow_html=True)
