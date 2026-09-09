import os
base = r"C:\Users\admin\WorkBuddy\courseware-site\lessons"
dirs = ["25-math-trig-omega-range-1","26-math-trig-omega-range-2","27-math-trig-omega-range-3",
        "28-math-trig-omega-range-4","29-math-trig-omega-range-5","30-math-trig-omega-range-6","31-math-trig-omega-range-7"]
for d in dirs:
    p = os.path.join(base, d, "index.html")
    c = open(p,"r",encoding="utf-8").read()
    hasTouch = "touchstart" in c and "touchmove" in c and "touchend" in c
    hasPassive = ",{passive:false}" in c
    hasWheel = "'wheel'" in c
    hasSlider = "omegaSlider" in c
    hasCanvas = "canvas" in c
    hasKaTeX = "katex@0.16.9" in c
    hasMeta = 'meta name="number"' in c
    hasBack = "mcjc4.github.io/courseware" in c
    badBraces = "}},{{passive" in c
    ok = all([hasTouch,hasPassive,hasWheel,hasSlider,hasCanvas,hasKaTeX,hasMeta,hasBack]) and not badBraces
    sz = len(c)
    mark = "PASS" if ok else "FAIL"
    print(f"[{mark}] {d} ({sz}B) touch={hasTouch} passive={hasPassive} wheel={hasWheel} katex={hasKaTeX} badBraces={badBraces}")
