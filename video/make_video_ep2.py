"""Episódio 2: compatibilidade de preço na inexigibilidade.

Narração sintética (espeak-ng + voz MBROLA br4), legendas e cartões de texto
sobre o Fundo_Gelisete. Requer: ffmpeg, espeak-ng, mbrola-br4, Pillow.
Uso: python3 video/make_video_ep2.py
"""
import os
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 1280, 720, 24
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
ACCENT = (196, 86, 44)
NAVY = (36, 70, 128)
DARK = (30, 30, 30)

ABERTURA = os.path.join(ROOT, "Abertura_2.mp4")
FUNDO = os.path.join(ROOT, "Fundo_Gelisete.png")
OUT = os.path.join(ROOT, "video", "Episodio2_Compatibilidade_de_preco.mp4")

VOICE, SPEED, GAP = "mb-br4", 148, 0.7
INTRO_DUR, XF = 8.0, 1.0

# Cada cena: cartão (título + itens) e falas. Cada fala tem o texto da
# legenda e, quando diferente, o texto escrito para a pronúncia da voz.
SCENES = [
    {
        "tag": "Episódio 2",
        "title": "Compatibilidade de preço na inexigibilidade",
        "items": [],
        "lines": [
            ("Olá! Eu sou a Gelisete.", None),
            ("Hoje vamos falar de um ponto que gera muitas dúvidas: "
             "a comprovação da compatibilidade de preço nos processos de inexigibilidade.", None),
        ],
    },
    {
        "tag": "O conceito",
        "title": "Inexigibilidade afasta a competição, não a justificativa de preço",
        "items": ["Fornecedor exclusivo", "Notória especialização", "Competição inviável"],
        "lines": [
            ("Na inexigibilidade, a licitação é inviável porque não há competição possível.", None),
            ("Por exemplo: um fornecedor exclusivo ou um profissional de notória especialização.", None),
            ("Mas atenção: a inexigibilidade afasta a competição, "
             "não afasta o dever de justificar o preço.", None),
        ],
    },
    {
        "tag": "Lei 14.133/2021",
        "title": "Art. 72: o processo deve conter",
        "items": ["Estimativa de despesa (inciso II)", "Justificativa de preço (inciso VII)"],
        "lines": [
            ("A Lei 14.133 de 2021, no artigo 72, exige que o processo de contratação direta "
             "seja instruído com a estimativa de despesa e com a justificativa de preço.",
             "A Lei quatorze mil cento e trinta e três, de dois mil e vinte e um, no artigo "
             "setenta e dois, exige que o processo de contratação direta seja instruído com "
             "a estimativa de despesa, e com a justificativa de preço."),
        ],
    },
    {
        "tag": "Art. 23, § 4º",
        "title": "Quem comprova é o contratado",
        "items": ["Preços conformes aos praticados", "Em contratações semelhantes",
                  "Objetos de mesma natureza"],
        "lines": [
            ("O artigo 23, parágrafo 4º, mostra o caminho: quando não for possível usar "
             "os parâmetros comuns de pesquisa de preços,",
             "O artigo vinte e três, parágrafo quarto, mostra o caminho: quando não for "
             "possível usar os parâmetros comuns de pesquisa de preços,"),
            ("o contratado deve comprovar que seus preços estão em conformidade com os "
             "praticados em contratações semelhantes.", None),
        ],
    },
    {
        "tag": "Como comprovar",
        "title": "Documentos aceitos",
        "items": ["Notas fiscais emitidas a outros contratantes",
                  "Período de até 1 ano antes da contratação",
                  "Ou outro meio idôneo (contratos, empenhos)"],
        "lines": [
            ("Essa comprovação pode ser feita com notas fiscais emitidas para outros "
             "contratantes, no período de até um ano antes da contratação,", None),
            ("ou por outro meio idôneo, como contratos e empenhos de outros órgãos.", None),
        ],
    },
    {
        "tag": "Por que importa",
        "title": "Preço justificado protege todos",
        "items": ["✓ Evita sobrepreço", "✓ Dá transparência", "✓ Segurança diante do controle"],
        "lines": [
            ("Por que isso é tão importante? Primeiro, porque protege contra sobrepreço:", None),
            ("o fornecedor exclusivo não pode cobrar de você mais do que cobra dos outros.", None),
            ("Segundo, porque dá transparência e segurança ao processo diante dos órgãos de controle.",
             None),
        ],
    },
    {
        "tag": "Art. 73",
        "title": "Responsabilidade solidária",
        "items": ["Contratação direta indevida", "Com dolo, fraude ou erro grosseiro",
                  "Contratado e agente respondem pelo dano"],
        "lines": [
            ("E terceiro, porque há responsabilidade. Pelo artigo 73,",
             "E terceiro, porque há responsabilidade. Pelo artigo setenta e três,"),
            ("se a contratação direta for indevida, com dolo, fraude ou erro grosseiro,", None),
            ("o contratado e o agente público respondem solidariamente pelo dano causado.", None),
        ],
    },
    {
        "tag": "Na prática",
        "title": "Checklist antes de contratar",
        "items": ["1. Peça os documentos de preço", "2. Confira se os objetos são semelhantes",
                  "3. Verifique as datas", "4. Registre tudo no processo"],
        "lines": [
            ("Então, fica a dica: peça os documentos de preço ao fornecedor antes de contratar,",
             None),
            ("confira se os objetos são realmente semelhantes, verifique as datas, "
             "e registre tudo no processo.", None),
        ],
    },
    {
        "tag": "Lembre-se",
        "title": "Exclusividade não é cheque em branco",
        "items": ["Preço justificado é contratação segura."],
        "lines": [
            ("Lembre-se: exclusividade não é cheque em branco.", None),
            ("Preço justificado é contratação segura. Até o próximo episódio!", None),
        ],
    },
]


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        test = f"{cur} {word}".strip()
        if draw.textlength(test, font=fnt) <= max_w or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = word
    return lines + [cur]


def background(path):
    """Fundo com a Gelisete deslocada à direita, abrindo espaço para os cartões."""
    img = Image.open(FUNDO).convert("RGB")
    img = img.resize((round(img.width * H / img.height), H), Image.LANCZOS)
    shift = 300
    canvas = Image.new("RGB", (W, H))
    # Estende a borda esquerda da parede para preencher o espaço aberto.
    edge = img.crop((0, 0, 1, H)).resize((shift + 20, H))
    canvas.paste(edge, (0, 0))
    canvas.paste(img.crop((20, 0, W - shift + 20, H)), (shift, 0))
    canvas.save(path)


def overlay(path, scene, subtitle):
    """Cartão da cena + legenda, em PNG transparente."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x, max_w = 56, 470
    f_tag, f_title, f_item = font(FONT_BOLD, 24), font(FONT_BOLD, 38), font(FONT, 26)
    tw = d.textlength(scene["tag"], font=f_tag) + 40
    d.rounded_rectangle((x, 70, x + tw, 116), radius=23, fill=NAVY)
    d.text((x + tw / 2, 93), scene["tag"], font=f_tag, fill="white", anchor="mm")
    y = 140
    for line in wrap(d, scene["title"], f_title, max_w):
        d.text((x, y), line, font=f_title, fill=DARK)
        y += 48
    d.rectangle((x + 2, y + 10, x + 112, y + 16), fill=ACCENT)
    y += 40
    for item in scene["items"]:
        for i, line in enumerate(wrap(d, item, f_item, max_w - 24)):
            if i == 0 and not item[0] in "✓123456789":
                d.ellipse((x + 2, y + 11, x + 12, y + 21), fill=ACCENT)
            d.text((x + 24, y), line, font=f_item, fill=(60, 60, 60))
            y += 34
        y += 8

    f_sub = font(FONT_BOLD, 28)
    lines = wrap(d, subtitle, f_sub, W - 200)
    box_h = 20 + 38 * len(lines)
    top = H - 36 - box_h
    d.rounded_rectangle((70, top, W - 70, H - 36), radius=14, fill=(0, 0, 0, 175))
    for i, line in enumerate(lines):
        d.text((W / 2, top + 10 + 38 * i + 17), line, font=f_sub, fill="white", anchor="mm")
    img.save(path)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", path], capture_output=True, text=True, check=True)
    return float(out.stdout)


def main():
    tmp = tempfile.mkdtemp()
    bg = os.path.join(tmp, "bg.png")
    background(bg)

    audio_list, ov_list, t = [], [], 0.0
    silence = os.path.join(tmp, "gap.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    "anullsrc=r=48000:cl=mono", "-t", str(GAP), silence], check=True)
    n = 0
    for scene in SCENES:
        for shown, spoken in scene["lines"]:
            raw, wav = os.path.join(tmp, f"r{n}.wav"), os.path.join(tmp, f"a{n}.wav")
            subprocess.run(["espeak-ng", "-v", VOICE, "-s", str(SPEED), "-a", "70", "-w", raw,
                            spoken or shown], check=True)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af",
                            "aresample=48000,highpass=f=80,lowpass=f=7000",
                            "-ac", "1", wav], check=True)
            png = os.path.join(tmp, f"o{n}.png")
            overlay(png, scene, shown)
            dur = duration(wav) + GAP
            audio_list += [wav, silence]
            ov_list.append((png, dur))
            t += dur
            n += 1
    content_dur = t

    with open(os.path.join(tmp, "audio.txt"), "w") as f:
        f.writelines(f"file '{p}'\n" for p in audio_list)
    with open(os.path.join(tmp, "ov.txt"), "w") as f:
        for p, dur in ov_list:
            f.write(f"file '{p}'\nduration {dur:.3f}\n")
        f.write(f"file '{ov_list[-1][0]}'\n")
    narration = os.path.join(tmp, "narr.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i",
                    os.path.join(tmp, "audio.txt"), "-af", "loudnorm=I=-16", "-ar", "48000",
                    narration], check=True)

    off = INTRO_DUR - XF
    total = off + content_dur + 1.5
    frames = int((total - off) * FPS)
    zoom = (f"zoompan=z='1+0.04*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={frames}:s={W}x{H}:fps={FPS}")
    fc = (
        f"[0:v]scale={W}:{H},fps={FPS},format=yuv420p,setsar=1[a];"
        f"[1:v]{zoom},format=rgba[bgz];"
        f"[2:v]fps={FPS},format=rgba,fade=t=in:st=0:d=0.6:alpha=1[ov];"
        f"[bgz][ov]overlay=0:0:shortest=0:eof_action=pass,format=yuv420p,setsar=1,"
        f"trim=duration={total - off}[c];"
        f"[a][c]xfade=transition=fade:duration={XF}:offset={off},"
        f"fade=t=out:st={total - 1}:d=1[v];"
        f"[0:a]atrim=duration={INTRO_DUR},afade=t=out:st={INTRO_DUR - 1.5}:d=1.5[ia];"
        f"[3:a]adelay={int(INTRO_DUR * 1000)}|{int(INTRO_DUR * 1000)},aformat=channel_layouts=stereo[na];"
        f"[ia][na]amix=inputs=2:duration=longest:normalize=0,atrim=duration={total},alimiter=limit=0.89[aout]"
    )
    subprocess.run([
        "ffmpeg", "-v", "error", "-y",
        "-i", ABERTURA,
        "-loop", "1", "-i", bg,
        "-f", "concat", "-safe", "0", "-i", os.path.join(tmp, "ov.txt"),
        "-i", narration,
        "-filter_complex", fc, "-map", "[v]", "-map", "[aout]",
        "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", OUT,
    ], check=True)
    print("Gerado:", OUT)


if __name__ == "__main__":
    main()
