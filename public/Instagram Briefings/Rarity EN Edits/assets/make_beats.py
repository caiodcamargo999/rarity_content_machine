import json, re, sys
def norm(t): return re.sub(r'[^a-z0-9]', '', t.lower())
class Words:
    def __init__(self, path): self.w = json.load(open(path)); self.n = [norm(x['text']) for x in self.w]
    def find(self, phrase, nth=1, end=False, back=0):
        toks = [norm(t) for t in phrase.split()]
        c = 0
        for i in range(len(self.n) - len(toks) + 1):
            if self.n[i:i+len(toks)] == toks:
                c += 1
                if c == nth:
                    j = i + len(toks) - 1
                    return round(self.w[j]['end'] if end else self.w[i]['start'], 2)
        raise SystemExit(f"phrase not found: {phrase!r} (nth={nth})")
def build(vid):
    W = Words(f'words_fix{vid}.json'); B = []
    def top(kind, at, dur, **p): B.append({"type": kind, "zone": "top", "start": at, "end": at + dur, "params": p})
    def low(kind, s, e, anchors=None, **p): B.append({"type": kind, "start": s, "end": e, "anchors": anchors or {}, "params": p})
    f, e = W.find, (lambda ph, n=1: W.find(ph, n, end=True))
    if vid == '01':
        low("title", 0.15, 3.3, {}, kicker="DTC GROWTH", title="Scale without bleeding cash", size=70)
        top("nametag", 3.5, 3.4)
        top("icon", f("platform ROAS")-0.05, 2.2, icon="chart")
        top("icon", f("real profit")-0.05, 2.2, icon="dollar", side="left")
        low("stat", f("5 million")-0.4, e("on Google")+0.5, {"s0": f("5 million"), "s1": f("8x"), "s2": f("10x")},
            stats=[["$5M", "verified revenue"], ["8x", "ROAS on Meta"], ["10x", "ROAS on Google", True]])
        top("icon", f("book your free growth audit")-0.05, 2.4, icon="calendar")
        top("icon", f("One Number Model")-0.05, 2.4, icon="target")
        low("level", f("Level 1"), e("against MER")+0.3, num="1", title="Performance media", sub="Meta + Google as one budget · MER")
        low("vs", f("flat fee")-0.1, e("your spend")+0.4, {"right": 0.15, "strike": f("never a percentage")-f("flat fee")+0.1},
            left="% of ad spend", right="flat fee", lsub="paid more when you spend more", rsub="never a % of your spend")
        top("icon", f("paid to make you")-0.05, 2.2, icon="trophy")
        low("level", f("Level 2"), e("production costs")+0.3, num="2", title="AI-native creative", sub="dozens of variations a week")
        low("stat", f("35 hooks")-0.3, e("17x ROAS")+0.6, {"s0": f("35 hooks"), "s1": f("3 winners"), "s2": f("17x ROAS")},
            stats=[["35", "hooks in 7 days"], ["3", "winners"], ["17x", "ROAS", True]])
        low("level", f("Level 3"), e("Google Drive folder")+0.3, num="3", title="UGC", sub="real creators · briefed & edited to convert")
        top("icon", f("one team looking")-0.05, 2.4, icon="users")
        top("icon", f("No more media buyers")-0.05, 2.6, icon="cross")
        low("stat", f("If you are a DTC")-0.1, e("million a year")+0.4, {"s0": f("1 to 10 million")}, stats=[["$1M–$10M", "a year · DTC brands", True]])
        top("icon", f("Meta roller coaster")-0.05, 2.0, icon="arrow_up", side="left")
        low("cta", f("click the link and apply")-0.1, e("growth audit", 2)+0.6, {}, line1="Free growth audit", line2="Click the link", line3="media · creative · funnel vs your real P&L")
        low("checklist", f("We'll go through")+0.0, e("what we'd change first")+0.6,
            {"r0": f("your media"), "r1": f("your creative"), "r2": f("your funnel")},
            rows=[["Your media", "vs real P&L"], ["Your creative"], ["Your funnel"]])
        top("icon", f("If we're not a fit")-0.05, 2.2, icon="shield")
        top("icon", f("See you on the call")-0.2, 2.2, icon="calendar")
    if vid == '02':
        low("title", 0.15, 3.2, {}, kicker="ECOMMERCE", title="ROAS vs real profit", size=84)
        top("nametag", 3.4, 3.4)
        low("stat", max(3.4, f("if your ROAS looks good")-0.1), e("profit doesn't")+0.3, {"s0": f("ROAS looks good"), "s1": f("profit doesn't")},
            stats=[["ROAS", "looks good"], ["Profit", "doesn't", True]])
        top("icon", f("wrong number")-0.05, 2.0, icon="cross")
        low("channels", f("Your Meta dashboard")-0.1, e("same results")+0.4, {"flat": f("bank account")}, names=["Meta", "Google"], metric="Bank account", flat_label="not the same")
        top("icon", f("bank account")-0.05, 2.0, icon="dollar")
        low("checklist", f("doesn't know your real margins")-0.1, e("your refunds")+0.4,
            {"r0": f("real margins"), "r1": f("shipping costs"), "r2": f("your refunds")},
            rows=[["Your real margins"], ["Your shipping costs"], ["Your refunds"]], mark="x")
        top("icon", f("how much profit you need to keep")-0.05, 2.4, icon="shield")
        low("cac", f("something called")-0.0, e("still make money")+0.5, {"marker": f("the most you can pay"), "profit": f("still make money")},
            title="Maximum Allowable CAC", sub="the most you can pay for a new customer", ceiling="ceiling", profit_text="and still make money")
        low("ceiling", f("For example")-0.1, e("make it worse")+0.5,
            {"p42": f("customers for 42"), "p62": f("paying 62")}, title="Maximum Allowable CAC", ceiling=55, lo=20, hi=75,
            points=[[42, "p42", True], [62, "p62", False]], labels=["room to scale", "makes it worse"])
        low("call", f("free 45-minute")-0.1, e("may be leaking")+0.3, {}, big="45", kicker="free profit diagnostic", foot="see where your profit leaks", unit="min")
        top("icon", f("tell you")-0.05, 2.0, icon="check")
        low("cta", f("Click below and apply")-0.1, f("here's what you get")-0.1, {}, line1="Free profit diagnostic", line2="Click below to apply", line3="45 minutes · based on your real numbers")
        low("checklist", f("here's what you get")+0.0, 80.7,
            {"r0": f("your Maximum Allowable CAC"), "r1": f("your customer economics"), "r2": f("the biggest area")},
            rows=[["Your Maximum Allowable CAC"], ["Your customer economics"], ["Your biggest profit leak"]])
    if vid == '03':
        low("title", 0.15, 3.3, {}, kicker="CASE STUDY", title="One brand. Real profit.", size=80)
        top("nametag", 3.5, 3.4)
        top("icon", f("platform ROAS")-0.05, 2.4, icon="chart")
        low("stat", max(3.5, f("2 million")-0.5), e("up 4x")+0.5, {"s0": f("2 million"), "s1": f("8x ROAS"), "s2": f("down 35%"), "s3": f("up 4x")},
            stats=[["$2M", "verified revenue"], ["8x", "ROAS", True], ["-35%", "CAC"], ["4x", "order volume"]])
        top("icon", f("Meta roller coaster")-0.05, 2.4, icon="arrow_up", side="left")
        low("cta", f("click the link and book")-0.1, e("growth audit")+0.5, {}, line1="Free growth audit", line2="Click the link", line3="book it below")
        top("icon", f("book your free growth audit")-0.05, 2.4, icon="calendar")
        top("icon", f("One Number Model")-0.05, 2.4, icon="target")
        low("strike", f("Most agencies charge you")-0.1, e("profitable or not")+0.3, {"strike": f("the more they make")-f("Most agencies charge you")},
            big="%", label="of your ad spend", sub="the more they spend, the more they make")
        low("checklist", f("three vendors")-0.2, e("raw clips")+0.5,
            {"r0": f("a media buyer"), "r1": f("a creative studio"), "r2": f("a UGC shop")},
            rows=[["Media buyer", "chasing ROAS"], ["Creative studio", "chasing engagement"], ["UGC shop", "sending raw clips"]], mark="x")
        low("stat", f("one team, one number")-0.1 if False else f("one team one number")-0.1, e("three levers")+0.4,
            {"s0": f("one team"), "s1": f("one number"), "s2": f("three levers")}, stats=[["1", "team"], ["1", "number"], ["3", "levers", True]])
        low("vs", f("flat fee")-0.1, e("your spend")+0.4, {"right": 0.1, "strike": f("never a percentage")-f("flat fee")+0.1},
            left="% of ad spend", right="flat fee", lsub="the more you spend, the more they make", rsub="never a % of your spend")
        low("level", f("performance media")-0.1, e("contribution margin")+0.3, num="1", title="Performance media", sub="Meta + Google · one budget · MER")
        low("level", f("AI-native creative")-0.1, e("production cost")+0.3, num="2", title="AI-native creative", sub="dozens of new ad variations a week")
        low("level", f("UGC real creators")-0.1, e("edited to convert")+0.3, num="3", title="UGC", sub="real creators · briefed & edited to convert")
        low("level", f("direct access")-0.1, e("cash flow")+0.3, num="+", title="Senior operators", sub="inventory · margin · cash flow")
        top("icon", f("senior operators")-0.05, 2.6, icon="users")
        top("icon", f("No junior")-0.05, 2.0, icon="cross")
        low("stat", f("So you get one team")-0.1, e("your profit")+0.5, {"s0": f("one team that"), "s1": f("one number everyone")},
            stats=[["1", "team owns the growth"], ["1", "number: your profit", True]])
        top("icon", f("your profit")-0.1, 2.2, icon="dollar", side="left")
        low("stat", f("One brand ran")-0.1, e("10x ROAS")+0.5, {"s0": f("10 million"), "s1": f("10x ROAS")},
            stats=[["$10M", "in sales"], ["10x", "ROAS", True]])
        low("stat", f("35 new hooks")-0.3, e("17x ROAS")+0.6, {"s0": f("35 new hooks"), "s1": f("3 winners"), "s2": f("17x ROAS")},
            stats=[["35", "new hooks in 7 days"], ["3", "winners"], ["17x", "ROAS", True]])
        low("stat", f("a third brand")-0.1, e("cold traffic")+0.5, {"s0": f("6x ROAS"), "s1": f("under 20")},
            stats=[["6x", "ROAS on TikTok", True], ["<$20", "CAC · cold traffic"]])
        low("stat", f("1 million to 10 million")-0.2, e("a year")+0.3, {"s0": f("1 million")}, stats=[["$1M–$10M", "a year · growth partner", True]])
        low("cta", f("click the link and apply")-0.1, e("growth audit", 2)+0.6, {}, line1="Free growth audit", line2="Click the link", line3="media · creative · funnel vs your real P&L")
        low("stat", f("two to four business days")-0.1, e("real P&L")+0.4, {"s0": f("two to four")}, stats=[["2–4", "business days to audit", True]])
        top("icon", f("business partner")-0.05, 2.4, icon="users")
        top("icon", f("See you on the other side")-0.2, 2.4, icon="play")
    # sanity: lower beats must not overlap
    lo = sorted([b for b in B if b.get("zone") != "top"], key=lambda b: b["start"])
    for a, b in zip(lo, lo[1:]):
        if b["start"] < a["end"]:
            a["end"] = b["start"] - 0.05
    tp = sorted([b for b in B if b.get("zone") == "top"], key=lambda b: b["start"])
    for a, b in zip(tp, tp[1:]):
        if b["start"] < a["end"]:
            a["end"] = b["start"] - 0.05
    return B
for v in ('01', '02', '03'):
    B = build(v)
    json.dump(B, open(f'beats_{v}.json', 'w'), indent=1)
    print(v, len(B), 'beats', sum(1 for b in B if b.get('zone') == 'top'), 'top')
