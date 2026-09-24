import sys, pymupdf
pdf, out = sys.argv[1], sys.argv[2]
doc = pymupdf.open(pdf)
for i, pg in enumerate(doc):
    pg.get_pixmap(dpi=70).save(f"{out}_p{i+1}.png")
print("pages", len(doc))
