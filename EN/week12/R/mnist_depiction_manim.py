"""MNIST concept — from pixels to a ten-class neural-network diagram.

Manim Community Edition, standalone. The 12 embedded 28×28 thumbnails
are resized samples from the scikit-learn handwritten-digits collection;
therefore they are MNIST-*style* examples, not samples from official MNIST.
The NN scores and connections are deliberately illustrative, NOT inferred
by a trained network. No downloads, pretrained files, or 3b1b dependencies.

Render:
  manim -pql mnist_depiction_manim.py MNISTDepictionLight
  manim -pqh mnist_depiction_manim.py MNISTDepictionLight
  manim -p -r 1920,1080 mnist_depiction_manim.py MNISTDepictionLight

Designed for Manim's default 16:9 frame, at 1920x1080 if requested.
"""

import base64
import zlib
import numpy as np
from manim import *

# Statistics 101 semantic palette; same as the other Week 12 Manim scenes.
BG      = "#FBFCFE"
INK     = "#182230"
MUTED   = "#667085"
LINE    = "#D9E1EA"
PANEL   = "#F3F6FA"
BLUE    = "#1F6FEB"       # input / observations
ORANGE  = "#C65D09"       # hidden model
GREEN   = "#18864B"       # output / result
PURPLE  = "#7B4AB5"       # signal propagation
RED     = "#C93838"

# Twelve genuine handwritten-digit examples (from sklearn load_digits),
# upscaled from their native 8×8 images to 28×28 for this conceptual scene.
# Encoded in this file, so NO external images/datasets are needed to render.
# This is explicitly not the official MNIST data collection.
DIGIT_LABELS = (7, 2, 1, 0, 4, 9, 5, 6, 8, 3, 2, 7)
DIGIT_PAYLOAD = (
    "c-nPZc|25Y6ed{;*~>1WETvHr4He3gkhPF4lq^X|%94<fE&HId?-V29W0a8WTXuycOXyQ*(f#fnX6DZF-GA!m@owim=Q-y&F"
    "DfeB$1QJix1eVk0Kef}59Br~!pFQ%{c=cg*Aj#c5n<Z}4xhUgl2*|^4MKkh@^2~PG1kMz9tq`d+gjU({{?{M-eO;6CLAVuF}"
    "iYW4Okv%cssiEZK}Qat_mKLa>{I71c0xNc|}d*(?fMn+z9Il8waMpc#X;MxA)2)p6N())fA@2uXjkt%-Zt&@%=)|QA10OK1g"
    "mF{5Gjs1%!Cnp=pEz$9^_A@1}x(w6t5Ge;DNBXMq0D)4S=3&@IfodlhwW*R2CTTc5Zbh1-RS{eb4>p!E8$kYUzpE_1^mdMU$"
    "O$<;$xdji0ymmmRRk~EKg(ee4u1_U%X@(?DJGEV6Gxd{NDn;vPg;2^r)svb2s1o%+?(CQ#94r35e_bgx9K&G1V0xgwz@l(<X"
    "9k&iG>jCco7)W$AS4Z$M;4vB=#3>V(@Ol7P&(-4N+Cc|D9IFTddB#3x4)`3zM@90{a|j_+FD3VXYjt5J#i*#+4`?~YW7><X$"
    "T2Dg8B?#Ayu2`77IKUp=^Ppp9bk8qfgEGj4o*+FWvswQ4pDKMKdDHzIkbz80>*u%xFO}d05t`Oiq{F<oT|r8`eQ~J-+rtqdt"
    "*#xI7qf}*sl+Z4LrVboMbOtih&#BrYb_M5Ja2VCZZiRjK%(pHzXLa64@DH8b64;*Iu}zfc_w39D<qo{qx^d5L=BDBbrkPdC@"
    "<$xV*9%yxX6T#E4DFDJrL`XXEkc?H^!1OoaUGjQccQ@~42&fZY@fBcOe&czmVfwjc%Uuv>cb^xSJ#UJ7%b&+3`|I{M6JCpjk"
    "M(fs4*)ay6{GILYW9(^<o{BBEfk|(=&IswCH0I*VIuSmAs7G9)#GXPA7ALk;wTn>fHNkah8<|0JCk$smRH+)|GoTWocj;X};"
    "eq9``_B~7vaamRU2EH{vwwEG1wb1D>aIv}aP-_JN0Z~aQF#(QEmY^0p=Uce~03Wk_?F_Z_EU!9RYRQXkP#uH3YbN9_qv>}&J"
    "bmuRXQoHG8pv^N+};uAv|bRKseGKAUQ}M+)|l&SEXTPqr-&|gPGG99cWC_c*RP|`Z=cz>NuMkSO_L`9!Z(L@!}B1mz^Twd81"
    "|#W<q$pyxs(F?VA#*9YX~NyQ?eVSbpD3e>h`JKq;bY>h-&}!KN!ooxVJ0+gE4A`)<Ue+NCDe^D&WQJ|6uIe4{I0x2NSuRKlB"
    "H?p4uJ~j8QS92Yb5L-s&R6B+npjQMii5>b&6NsF``Bl&vB=H>^^9<2e6TJS3udB_R1l_Zk*jN88I1sDer5?z5hGoH2hFS?t|"
    "TFo<qK`@eWY|H?HI*g{|zwFgy$-*DJkrp_){D9G4_WxjkjGXEEgWoWX&16JkYHJ`}5mN_hzrVc0G9TJM_23Gf;eZ*o<Pcg!&"
    "nuT|dIKnt_hyn(|Tj>z@dN<}&V<L-*U9K(vi?P`Kvx=Qlg`Ny!vncumo&E9gtz;OxacVb2lj*ADNr2_-Lkwh{Qq$dJ!ONt4y"
    "AV3zTVD+k(vb}EPN~q%k3Due&PAGY4%t3}PBB+@Pe*{1eGrzBO`y4#szZ%PX;RD;-I8-fiirY4(jB^8-BseQ$VZ-!n8gj_+9"
    "#V59MnZfkIp7%`SA4;@cn&dlo4r?+i(B0Wy5Di!jQ!FWIYqx^<%?dRtqogg&%!~%=M~oz~9BGj}u?|OYd79A$SEF!X#l7q>z"
    "^>5us72{IU$Ey?AW*S+5u1)pdqhX)38+dfGdPI*I383A2Z9!Ij?moRQ+@RgM4n4Q-6u4(-9qiO|ip`kfJ>+qyqwZ0*f8(M^A"
    "%MO;C3fmr7QeNoU^y}G}(1gZ#c>~)Le#fT;l>k2gx2KQ`VH~H?-MY+uk!lUF+_#FV+1J8mcp)+{;rZVw{_GUKQ!ifw4-Kfn+"
    "6|B3cm2Rh`qwd?v;2eX)={<<uR)%UaDGQ(I)WloIamJyx1OvL~o(6Q^yU)2r=M{!&;xE#y9dwi^BWMwBZFf{<U8)g2U7NOno"
    "SbHl0RPKpcsKWLSK&o`Ix}trfPc~Vw0WrLk2=R!_70R-;tAp0KcGjq<=!<trGGoOad2`l-wZ!avjn88&)t~(wBq)K_1_CUkM"
    ";5EDJO#mT>JiQejZCsUofGB2u0kk99jH@FBNMa*&*;Q#jEX;*}AYnJ`;^;H+5iT48vZ{n?)b6oHbZ--$IrR9!ji|Ca3|dFEv"
    "G9I!f%^v;x|X-b2{RtNTXc<b@r-tZ5)BNSl>HM6imTv<piO)}e$6o-p@DWrgbOprTM1Tn)=8Es4;fP)F`COnBAVSsSNMVI05"
    "X%TG%)U0Igg<hAL6J569ZTByH+AdOBMj*|~Mpwuyyq9edSQqf9Zh-rh;7*Kv0L0rKwOY3_i)r?^CgOe<AxhQBD5RXbJ05j{)"
    "Qkw(BJC*S+t4#6s&Yb|h=9x<npHMwzus_??E~e+tY>6XM03Pu>t*d`7SNS-_^{oGBiFZ^Jp@RjrFL*!Q@c~)jZWdZ|ywvz`c"
    "S|Rz7Ci-?tO!*BDYc&iS#}3;`D447Zaj!BVxBi+Q_nKSM^$L^{LB*i(V##4=xdwU@UyO1bKDu3CA0(U7Je;`jc<ya{-@3=n}"
    "s%`h>FXThMun09;`M378?^BaM)HZNsX%k5s~5X4Un}*D`TCtq;WQ-Vdj%Os;H!>771=?I?F>}PH+clc}H&tl6mV*MSco0fyx"
    "vN?K*1_T1vcZ2b!nGjG`9ca|7wH+FW=m1x(C)9E(w!Q`{FcOqHo1**K;PIUhI7GMjUO#1Hwb^T#%@g~E$OTu;xZ>Qg>6{~an"
    "SRw^C#!j@!3Ub<iSuD|s~QSA)Kh`#bLSKEKHv~y&rHT}A=8wTWpIBijaY1E!ht<AL;dmiIeP6ux?(+t5%$itOuf4UQ$RoJLR"
    "B3HotVSAJluTkCJuFq#1h=3fx888ogFLF@YJOwS^$)K)Zqk&i&<_-D+EEPGO<iQQokM3FNzbgV(PCM1o{{<HE@#A(PFD16m^"
    "+c*mDqgr24|>&nrj_jGy$hUjN_;)qneKksC;c^Kx0zHE>CJfIQ?Ywk*49!QAC>WX0y4}*GX4y#Qfk+eYu~<pSyuMqRoCp=YI"
    "mxm3Qj68326EiHgxs2qhs%d<u`TJrQbD?z+b+EZT!p5p`ILPb#3>jWu=)BR}SH=&8c}aHn%j-PeWANB04|+@dI0#tps7Oap9"
    "tw0g{i7*C@Iu@6k;Iae_nb+AGe-1pO+zN%G75`&KZCNGrHseB;VEt#ccm-7|o3vfw%Q8<y&agczwr++U5=1?fl<xZ-$RZ+{C"
    "q&R(7m8TsK?_e1Tygd$BJgO!_wj;dyPKY*bK4Ols>kq70B^{(XGVQ<!e7T;r>Ft4>ws~%kZ@umCq+YgHq`Ikgteg@_TCsgC)"
    "%3t8`%H*3c4I;Lq-gVrwWN4$MQFiMXF@@4fJLGN%jFCcDS$LGu3aj775Y)wLTg(|e;cb&R7uZ0+rfY&#@dso>+9&nmkiVZ^B"
    "{?0&@08Cts%{a>EtA8&jX8JCU_FohUNtiiG+AGgkr-etzYE3`s!8JzG+r6!cf(HS01TnwwE;EWpV7KBpNm>5^7~)~HXZ-*VD"
    "M<8Y3_#d!rYu}aOUAWYLf>RXRlr4xk(v<darRXSQY?fCj8|2Qt{3+P^zuv=x~rHH{Ike(9@SP^!UlDXEx(3kg9;CVtYj?u|3"
    ">Oa69ifm(l}ukNPr$ygc0<t&C6a$2$_Ea$pt2{lM3;f&RXZrn)Rw8T|bq?2}smz_nq49{z|znm00f;b4nBp3fNfC|ymg>l&V"
    "%nf~+{^0#5%g9O_!A<XVRdYn~|pHt8Tg5wXBxe2>vM4Y>H&C@p^IHnv_N|RBi_-SAQUh?P(bz`T%Cyk)y{CHoUjfh$~b_pIa"
    "kF16?M4!hVk}OWovfny=0NQVz6>*P=ky}jOC<rt67g+6&J4Hj})-u}8;rWd-e^&;c1se+!<@bZecb|WNtU6cXazcpciaC^=9"
    "&dR3RN@&DWx=K5o{x1x;8P@$hD^#F^G4S`RHW3EV&GQ`sHhD^Qp#Y0iZ+RLbrdn~)7N7wyBfnOVFzy%yc-#93^_&tI~mhEJK"
    "g=<6F~txn?1eQoppyy7(u%<EM1y;?w}w*q3OnKUb8Y8t3X5PbnJGGz^4b4nob~lI<^DT_t+?60<PV_{Cy5e&=yh8K43Xsni9"
    "r*$QL9KjEBL6ix%eQ7tbBxfQ7qqAXqH?+gjVu+S%FBiuOg~&%z+A5!?=Q`9Bp_cqXUiQx1S*K=a*`e7N+$c<@#S_@nv$mU>K"
    "m$LIhi`Q|xMoWSS328y5`7?i(@t)p*zRx!FD5U-qBE`!+DLSIWY`4h(O4+|PwvrTb(WxCoA62;3<doAS2^X?JPdq>gu78|Q0"
    ")K_fJyk}>4-tm5N&G5uaJ6zX*%^nhDqg5&QT;1=d6u%uEE49LTDWl=DWnj4vlOO*uDzmbotH1TBG0yT^j@&H3yuti~E-HA@@"
    "^NycxyWAy&&j+hR|AsrD{3$eeG4Eb{}X9L=tFN4Rkrj^LBDS4`vT?gGGBdByc2BMbx6-6vFuIf2-NbKf99!02s3UKTbC;~E^"
    "!T5LZ1j%;UV}ApN5my4JXfpS5sKpj!+jMgy5bF_hKSLBA!;XLCiK1YamIGEYhwywRKhHMHv|tBP+lApIkjj$i>L;w%Mhb;mR"
    "n_fa3R`+OoY3#qkTOpg#NomdDBiY@L(d^t^g{$4CO7`<3JSXNT(wV|`rxvfp);hgcwCbB5J7Wq4h7yc3>Y_r5dB;mA(HK9Be"
    "m7x<i2I`5xd-PThdp#^twX_wTr04o#M1awVxNrJ;cxcBZc4SkZ8kyBRpsx;Qs@F*u7<2mb-)v@sF$3#O4C`q;v>ki#}Wl-Tg"
    "RpzHml0fKWowBeh4s%DBggU8s^y07$vZ>%Bd?cxiN!qat`@qm-N*dPNMK!!Dp!)_Y^~t)vY7QYe^}}=DzdpAlNo910ZG)m>Q"
    "3bDhy7Jsq_7RDrZ3@m2QK7*xdDYcf{^m;jBuyFL2ccoHX?eLRAvg3Sh_)ki+SV%~IW7GODj_<+_6X66tWp||k$KMxo+c$FMK"
    "~*NCn{aIWi7&=V=ynD=RFB`P$0G@y|8XDy5qyAv8HT)GiegTu%Gs?7y+}*WPyj42#K=TrsVq)N>a<kpfDoUw#U3HA*1~&aXd"
    "lV?h&#^uWfS6P=dZFe5cgHHl^P;vEj$&2u|3N+a&GLn~y-i#}Y3cDT1h^*(vY#;>-7m*2ccs<>}U3e|-W2Gm4(}Djn=A3HC)"
    "beOa0tthhsHfA83P$|a?u(9iI!2YPDt*FrliWzq9UYhAr_T?ZlSP`>bY^<%Z4EbMqJg8L6k3v!A()cyhHUL{=GM@G#wqSxO6"
    "z=sSsHS(tfYH=@6H1|cA9wKiUu*g3Ejr#7^2|+SJMk}O|0Q!Bs6M}r$cHuJ#bD;maDe#bqwXIx=!Jr}=NwPgg{&YdJ*QE)nS"
    "<{_lwvd4w#(ChRs{@H=$a@sv6+^DER&j~Kqt(viS5aUg-RmvGNFlk3SyTbQm*`V`6f`Hx*=JzZLTL$;$zKK@dAC*&i$Bdr8l"
    ";Spdfv~#Ds?*eC~+HtnwC{uKd2n)Uv#?fqk)ISKDm=;t^Kp=2WJ<C(v5jw33tz#Yr&{Ibal-?FA7tG%;81!cEwwTo%4Uz=i7"
    "@P-O!ic4R>CaGcn!RLUJ(MTX!FEkg=Y7JihU=ndPBE+N72CdjmOkvonSF9J%0TsQ=L7d63MI%x9CZg<wy#ku-7BhIW_C^(rW"
    "i)+cJ?9OQ_2g5$6W_C4;`*M+a6Mb_}WPz$NM<$eHwZ+&fGHX8AVzpK$oUhvOq9PBQQiFpHx_c(YtLVwscFfJwefz4^%c<>-u"
    "@H&iM*4D@8hLwge9k(-h3ndybi*1$Av$fDxfOy&n)JWxK@E!z*l$?whH}u=8IkPhr9;e}bZ(0WW4KF_y-rR`}u~p)tP#hf#u"
    "4yWZa#7<UhiKFiI{VN;77FYXYAO@-(k$9lS(rlUCwRRL_+4r)M!~6B<pM{5-+9^;W@L~wN|^$dP?Ty{L2WNEmraHrB!@UuZ$"
    "4@H1`LLfzSnIRL7F}&>zY~p-WjPSw3CY!W*HHakmC100O0qR=42;r6{O4_Ld_uO{|4Ky`Zd;25bf<`rK>>b+#o|cv3>TXk&g"
    "P8IWa!AYC?GKJ>pm0KQ=Nl_Tj_$<V0U(!VMil-6QRijxNc{dD%Jn4FG=j7x)<L!}E{i<+!xCppf*&Dd=f!wj$uX_*O!HA}Tq"
    "|%Li4D6>ZBk!51Xpyd~^ZxzXSS-bav_jaKFsW-|{AMiWbnorf(@-M=^gPynS&RAB4+7xb;-6ndTpk)womtrF_pN<BEHma(`o"
    "1lu01H-uw~ksae*Rp{#GL1;hqMsQ5RE;`o3P|qQ{3X-!JqH#NwE@+E^=5fgGS|=?lw(UVcVaH*e-2;mC=VysiHC7JqbgCF%2"
    "j<e0DY%nFVB0rf{X+r;SEJK>G66EeSn_ES?&OhD)Cp>YB;a!SRS9-N%H7I;MDIpaUdKiQbTHmbj*vds6s#YV4s1Tn0E=iJT|"
    "#*vd?CDI3~$e=5)i|Wll6NwgNGIyV{8=(KB$uN1&4eeZ%lPo6(Pi#O6umYl~0`&sGHi7up;xIM;W%`Ki5(c?`@-TfD`6P>`1"
    "!=u<HBO6z6KFAjZQ)@>c>DC9A+pmMv0%yfezFo&5tC4mm-AKDP237X1V|T!kp~Q(2^JD%ODp%WV{HhvTqAHRucml%yP|tYa+"
    "z)Myj^@IP*Rn8p"
)


def digit_images():
    raw = zlib.decompress(base64.b85decode(DIGIT_PAYLOAD.encode("ascii")))
    digits = np.frombuffer(raw, dtype=np.uint8).reshape(12, 28, 28).copy()
    return digits


def digit_mobject(gray, height):
    """Pixel brightness 0..255 (black background, white strokes)."""
    rgb = np.repeat(gray[:, :, None], 3, axis=2)
    return ImageMobject(rgb).set_height(height)


def label(text, size=16, color=MUTED, bold=False):
    return Text(text, font_size=size, color=color,
                weight=BOLD if bold else "NORMAL")


class MNISTDepictionLight(Scene):
    """12 examples → one 28×28 image → x with 784 entries → 10 classes."""

    def construct(self):
        self.camera.background_color = BG
        pictures = digit_images()
        chosen = 0  # digit 7
        chosen_digit = DIGIT_LABELS[chosen]

        self.frame_and_panels()
        gallery_images = self.draw_gallery(pictures)
        chosen_data = pictures[chosen]
        self.pixels_into_vector(chosen_data, gallery_images[chosen], chosen)
        self.animate_toy_network(chosen_digit)

        self.wait(1.6)

    # ================================================================
    # Composition and headings
    # ================================================================
    def frame_and_panels(self):
        title = label("How does a neural network see a handwritten digit?",
                      size=33, color=INK, bold=True).move_to([0, 3.54, 0])
        subtitle = label("28 × 28 pixels  →  784 numbers  →  hidden layers  →  ten digit scores",
                         size=19).move_to([0, 3.04, 0])
        stripe = Line([-6.60, 2.72, 0], [6.60, 2.72, 0],
                      stroke_width=3.4, color=BLUE)
        self.play(FadeIn(title), FadeIn(subtitle), Create(stripe), run_time=.85)

        panel_specs = [
            (-5.50, 3.02, BLUE),
            (-2.11, 3.43, PURPLE),
            (3.21, 6.81, ORANGE),
        ]
        panel_shapes = VGroup()
        borders = VGroup()
        for cx, width, color in panel_specs:
            box = RoundedRectangle(corner_radius=.15, width=width, height=5.86,
                                   stroke_color=LINE, stroke_width=1.4,
                                   fill_color=WHITE, fill_opacity=1)
            box.move_to([cx, -.50, 0])
            panel_shapes.add(box)
            top_y = box.get_top()[1] - .055
            borders.add(Line([cx-width/2+.16, top_y, 0],
                             [cx+width/2-.16, top_y, 0],
                             stroke_width=4, color=color))

        # Important: panels FIRST, text headers SECOND (no text masking).
        self.play(FadeIn(panel_shapes), FadeIn(borders), run_time=.65)

        headings = VGroup(
            label("EXAMPLES", 19, BLUE, True).move_to([-5.50, 2.02, 0]),
            label("PIXELS → VECTOR", 18, PURPLE, True).move_to([-2.11, 2.02, 0]),
            label("NEURAL NETWORK", 19, ORANGE, True).move_to([3.21, 2.02, 0]),
        )
        self.play(FadeIn(headings), run_time=.45)

    # ================================================================
    # Left: gallery of 12 example digits
    # ================================================================
    def draw_gallery(self, pictures):
        thumbs = []
        frames = VGroup()
        imgs = Group()

        x_cols = [-6.39, -5.50, -4.61]
        y_rows = [1.26, .13, -1.00, -2.13]
        for idx in range(12):
            c, r = idx % 3, idx // 3
            x, y = x_cols[c], y_rows[r]
            frame = RoundedRectangle(
                width=.81, height=.89, corner_radius=.09,
                stroke_color=LINE, stroke_width=1.3,
                fill_color="#0D1522", fill_opacity=1,
            ).move_to([x, y, 0])
            im = digit_mobject(pictures[idx], height=.77)
            im.move_to([x, y, 0])
            frames.add(frame)
            imgs.add(im)
            thumbs.append(im)

        foot = label("12 handwritten examples", size=15).move_to([-5.5, -3.06, 0])
        self.play(FadeIn(frames), LaggedStart(*[FadeIn(i) for i in imgs],
                  lag_ratio=.07), run_time=1.2)
        self.play(FadeIn(foot), run_time=.25)

        winner_ring = SurroundingRectangle(frames[0], color=BLUE,
                                            stroke_width=3.3, buff=.045,
                                            corner_radius=.11)
        self.play(Create(winner_ring), Flash(frames[0], color=BLUE,
                                            flash_radius=.53), run_time=.75)
        self.wait(.18)
        return thumbs

    # ================================================================
    # Center: selected photo, 28×28 grid, shortened 784-entry vector
    # ================================================================
    def pixels_into_vector(self, picture, original, chosen):
        # This copy REALLY originates at its thumbnail, not canvas center.
        enlarged = digit_mobject(picture, height=1.21)
        enlarged.move_to([-3.12, .54, 0])
        frame = RoundedRectangle(width=1.34, height=1.37,
                                 corner_radius=.07, stroke_color=PURPLE,
                                 stroke_width=2.1, fill_color="#0D1522",
                                 fill_opacity=1).move_to(enlarged)
        origin_note = label("28 × 28", 16, INK, True).move_to([-3.12, 1.48, 0])
        self.play(FadeIn(frame), TransformFromCopy(original, enlarged),
                  FadeIn(origin_note), run_time=1.05)
        # Ensure the enlarged digit persists after TransformFromCopy
        enlarged.set_opacity(1)
        self.add(enlarged)

        # A real grid of 28×28 sampling locations; small, vector strokes.
        grid_lines = VGroup()
        left = enlarged.get_center()[0] - 1.21/2
        top = enlarged.get_center()[1] + 1.21/2
        for k in range(1, 28):
            at = left + k*1.21/28
            grid_lines.add(Line([at, top, 0], [at, top-1.21, 0],
                                color="#DCE8FF", stroke_opacity=.20,
                                stroke_width=.48))
            at_y = top-k*1.21/28
            grid_lines.add(Line([left, at_y, 0], [left+1.21, at_y, 0],
                                color="#DCE8FF", stroke_opacity=.20,
                                stroke_width=.48))
        self.play(FadeIn(grid_lines), run_time=.4)

        # A handful of the 784 intensities, with actual numerical values.
        px = picture.flatten().astype(float)/255.0
        bright = np.flatnonzero(px > .42)
        mid = int(len(bright) // 2)
        indices = [0, 1, 2, None, int(bright[mid]), int(bright[min(mid+1,len(bright)-1)]), None, 783]
        ys = [1.35, .88, .41, -.06, -.53, -1.00, -1.47, -1.94]
        positions = []
        cell_groups = VGroup()
        for ix, yy in zip(indices, ys):
            if ix is None:
                cell_groups.add(label("⋮", 24, MUTED).move_to([-1.33,yy,0]))
                continue
            rect = RoundedRectangle(width=1.42, height=.39,
                                    corner_radius=.065, stroke_color=LINE,
                                    stroke_width=1, fill_color=PANEL,
                                    fill_opacity=1).move_to([-1.32, yy, 0])
            text = label(f"x{ix+1}  =  {px[ix]:.2f}", size=15, color=INK)
            text.move_to(rect)
            cell_groups.add(rect, text)
            positions.append((ix, rect.get_center()))

        short_arrow = Arrow([-2.48, .54, 0], [-2.17, .54, 0],
                            color=PURPLE, stroke_width=3.2,
                            buff=0, max_tip_length_to_length_ratio=.29)
        self.play(GrowArrow(short_arrow), FadeIn(cell_groups), run_time=.75)

        # The photo fragments into a small illustrative subset of its 784 pixels.
        # Pixel movements are schematic; listed x-values come from the image.
        rng = np.random.default_rng(12)
        sample = rng.choice(np.flatnonzero(picture > 32), size=38, replace=False)
        chips = VGroup()
        destinations = []
        for k, ix in enumerate(sample):
            row, col = divmod(int(ix), 28)
            xx = left + (col+.5)*1.21/28
            yy = top - (row+.5)*1.21/28
            v = picture[row, col]/255.0
            chip = Square(
                side_length=.045,
                stroke_width=0,
                fill_color=interpolate_color(BLACK, WHITE, float(v)),
                fill_opacity=1
            )
            chip.set_z_index(12)
            chip.move_to([xx, yy, 0])
            chips.add(chip)
            destination_y = float(ys[k%len(ys)])
            destinations.append(np.array([-1.32 + rng.normal(0,.18),
                                           destination_y + rng.normal(0,.08),0]))

        self.add(chips)
        # The photographed digit fades as sample pixels peel away. Keep a faint
        # ghost so the vector's origin remains apparent after the transition.
        self.play(
            LaggedStart(*[
                chip.animate \
                    .move_to(destinations[k]) \
                    .scale(1.65) \
                    .set_fill(BLUE, opacity=1)
                for k,chip in enumerate(chips)
            ], lag_ratio=.014),
            Succession(
                Wait(.95),
                enlarged.animate(run_time=.35).set_opacity(.20),
            ),
            grid_lines.animate.set_opacity(.22),
            run_time=1.3,
        )
        self.play(FadeOut(chips), run_time=.22)

        foot1 = VGroup(
            label("One image becomes", size=15, color=INK, bold=True),
            label("784 numbers", size=15, color=INK, bold=True)
        ).arrange(DOWN, buff=0.04)
        foot1.move_to([-2.11, -2.60, 0])
        self.play(FadeIn(foot1), run_time=.48)
        self.wait(.25)

    # ================================================================
    # Right: abbreviated input, 10-10-10 hidden units, 10 outputs
    # ================================================================
    def animate_toy_network(self, selected_digit):
        xs = [.43, 1.66, 2.90, 4.14, 5.39]
        y10 = np.linspace(1.07, -2.21, 10)
        y_input = np.array([1.07,.70,.34,-.02,-1.12,-1.48,-1.84,-2.21])
        ys = [y_input, y10, y10, y10, y10]

        names = ["784 inputs", "10", "10", "10", "10 digits"]
        sublabels = VGroup(*[
            label(name, 13, BLUE if i==0 else (GREEN if i==4 else ORANGE), True)
            .move_to([x,1.53,0])
            for i,(name,x) in enumerate(zip(names,xs))
        ])
        self.play(FadeIn(sublabels), run_time=.32)

        feed = Arrow([-.51, -.55, 0], [.17, -.55, 0], buff=0,
                     color=PURPLE, stroke_width=3,
                     max_tip_length_to_length_ratio=.13)
        self.play(GrowArrow(feed), run_time=.44)

        # Draw edges first so they stay behind all node circles/text.
        edge_layers = []
        faint_edges = VGroup()
        rng = np.random.default_rng(2026)
        for layer in range(4):
            edges = []
            from_y, to_y = ys[layer],ys[layer+1]
            for i, y1 in enumerate(from_y):
                for j, y2 in enumerate(to_y):
                    start = [xs[layer]+.12,y1,0]
                    end = [xs[layer+1]-.12,y2,0]
                    line = Line(start, end, color=LINE,
                                stroke_width=.72, stroke_opacity=.19)
                    faint_edges.add(line)
                    edges.append((i,j,line))
            edge_layers.append(edges)

        self.play(FadeIn(faint_edges), run_time=.7)

        circles = []
        for layer,(x,rows) in enumerate(zip(xs,ys)):
            g = VGroup()
            for y in rows:
                edge_color = BLUE if layer==0 else (GREEN if layer==4 else ORANGE)
                node = Circle(radius=.117, stroke_color=edge_color,
                              stroke_width=1.6, fill_color=WHITE,
                              fill_opacity=1)
                node.move_to([x,float(y),0])
                g.add(node)
            circles.append(g)

        dots = label("⋮", 23, BLUE, True).move_to([xs[0],-.60,0])
        digit_labels = VGroup(*[
            label(str(i), 14, MUTED, True).move_to([5.76,float(y),0])
            for i,y in enumerate(y10)
        ])

        self.play(FadeIn(VGroup(*circles)), FadeIn(dots), FadeIn(digit_labels),
                  run_time=.62)
        self.wait(.15)

        # Turn on input pixels. The values and later activations are only
        # illustrative: there are no trained weights anywhere in the script.
        illustrative = [
            np.array([.01,.12,.74,.96,.65,.21,.91,.38]),
            np.array([.30,.75,.10,.84,.43,.93,.56,.16,.79,.37]),
            np.array([.81,.10,.62,.30,.72,.57,.18,.88,.27,.48]),
            np.array([.44,.91,.65,.22,.18,.74,.54,.39,.80,.12]),
            np.array([.02,.03,.01,.04,.02,.02,.02,.79,.03,.02]),
        ]
        # Keep the bright output aligned with the pictured digit.
        base = np.array([.015,.025,.01,.04,.03,.02,.025,.025,.03,.02])
        base[selected_digit] = .78
        illustrative[-1] = base/base.sum()

        self.play(*[
            circle.animate.set_fill(BLUE, opacity=.09+.76*float(a))
            for circle,a in zip(circles[0],illustrative[0])
        ], run_time=.50)

        for k in range(4):
            # The weight thicknesses/activations are schematic (not inferred).
            # Reveal selected colored signals, enough to suggest the massive
            # fan-out without drawing 380 individually animated bright beams.
            if k == 3:
                # Final layer: all selected signals converge on digit 7
                selection = [
                    item for item in edge_layers[k]
                    if item[1] == selected_digit
                ]
            else:
                # Earlier layers: illustrative distributed signals
                selection = [
                    item for item in edge_layers[k]
                    if (item[0]*7 + item[1]*3 + k)%7 == 0
                ]
            flashes = [
                ShowPassingFlash(edge.copy().set_stroke(
                    color=PURPLE if k<3 else GREEN,
                    width=1.6+1.5*float(rng.random()), opacity=.94),
                    time_width=.53)
                for _,_,edge in selection
            ]
            self.play(LaggedStart(*flashes, lag_ratio=.015), run_time=1.06)

            to_color = ORANGE if k<3 else GREEN
            self.play(*[
                node.animate.set_fill(to_color, opacity=.08+.74*float(a))
                for node,a in zip(circles[k+1],illustrative[k+1])
            ], run_time=.62)

        # Ten output nodes represent scores for digits 0..9.
        best = selected_digit
        target = circles[-1][best]
        target_label = digit_labels[best]
        ring = SurroundingRectangle(target, color=GREEN,
                                     stroke_width=2.5, buff=.075,
                                     corner_radius=.06)
        final_note = label(f"Illustrative class: {best}", 20, GREEN, True)
        final_note.move_to([3.10,-2.83,0])
        caveat = label("Schematic activations · not a trained model", 13, MUTED)
        caveat.move_to([3.10,-3.23,0])
        self.play(Create(ring), target.animate.set_stroke(GREEN, width=3.0),
                  target_label.animate.set_color(INK), FadeIn(final_note),
                  FadeIn(caveat), run_time=.8)

