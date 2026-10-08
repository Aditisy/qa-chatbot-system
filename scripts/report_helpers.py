"""Build the Exercise 3 report in the supplied lab-report section order."""
from pathlib import Path
from xml.sax.saxutils import escape
import json
import shutil
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                              PageBreak, Preformatted, Image, HRFlowable)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'/'pdf'
OUT.mkdir(parents=True,exist_ok=True)
TARGET=OUT/'1GA23AI003_Exp2_QA_Chatbot_System.pdf'
DATE='8 October 2026'
BLUE=colors.HexColor('#225586')
PALE=colors.HexColor('#dce8f3')
GRAY=colors.HexColor('#777777')
WIDTH=A4[0]-96
styles={
    'body':ParagraphStyle('body',fontName='Times-Roman',fontSize=11,leading=14,spaceAfter=7,allowWidows=0,allowOrphans=0),
    'small':ParagraphStyle('small',fontName='Times-Roman',fontSize=10,leading=12,spaceAfter=5),
    'heading':ParagraphStyle('heading',fontName='Times-Bold',fontSize=14,leading=17,textColor=BLUE,spaceBefore=12,spaceAfter=5,keepWithNext=True),
    'sub':ParagraphStyle('sub',fontName='Times-Bold',fontSize=11.5,leading=14,textColor=BLUE,spaceBefore=7,spaceAfter=5,keepWithNext=True),
    'title':ParagraphStyle('title',fontName='Times-Bold',fontSize=16,leading=20,textColor=BLUE,alignment=1,spaceAfter=9),
    'code':ParagraphStyle('code',fontName='Courier',fontSize=8.5,leading=11,backColor=colors.HexColor('#f1f1f1'),borderPadding=8,spaceBefore=5,spaceAfter=10),
}
story=[]
md=['# LAB EXERCISE: 2','',f'Aditi S Yaranal | 1GA23AI003 | 7th Semester | AIML | Global Academy of Technology | {DATE}','']
def p(text,kind='body'):
    story.append(Paragraph(escape(text).replace('\n','<br/>'),styles[kind]))
    md.append(text+'\n')
def h(text):
    story.append(Paragraph(escape(text),styles['heading']))
    story.append(HRFlowable(width='100%',thickness=.7,color=BLUE,spaceAfter=7))
    md.append('## '+text+'\n')
def sub(text):p(text,'sub')
def bullet(text):
    story.append(Paragraph(escape(text),ParagraphStyle('bullet',parent=styles['body'],leftIndent=12,firstLineIndent=-8),bulletText='\u2022'))
    md.append('- '+text+'\n')
def table(rows,widths,header=True):
    cells=[[Paragraph(escape(str(c)).replace('\n','<br/>'),styles['small']) for c in row] for row in rows]
    t=Table(cells,colWidths=widths,repeatRows=1 if header else 0,hAlign='LEFT')
    commands=[('GRID',(0,0),(-1,-1),.45,colors.HexColor('#adb4ba')),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]
    if header:commands += [('BACKGROUND',(0,0),(-1,0),PALE)]
    t.setStyle(TableStyle(commands));story.append(t);story.append(Spacer(1,9))
    md.extend([' | '.join(str(c).replace('\n',' ') for c in row) for row in rows]);md.append('')
def code(text):
    block=Table([[Preformatted(text,styles['code'])]],colWidths=[WIDTH],hAlign='LEFT')
    block.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#f1f1f1')),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
    story.append(block);story.append(Spacer(1,9));md.extend(['```python',text,'```',''])
def page():story.append(PageBreak())
def diagram(labels):
    d=Drawing(WIDTH,66)
    bw=(WIDTH-36)/3
    for i,label in enumerate(labels):
        x=i*(bw+18)
        d.add(Rect(x,10,bw,48,fillColor=PALE,strokeColor=BLUE,strokeWidth=.6))
        for j,line in enumerate(label.split('\n')):
            d.add(String(x+bw/2,40-j*13,line,fontName='Times-Roman',fontSize=10,textAnchor='middle'))
        if i<2:
            d.add(Line(x+bw,34,x+bw+16,34,strokeColor=BLUE))
            d.add(Polygon([x+bw+16,34,x+bw+11,37,x+bw+11,31],fillColor=BLUE,strokeColor=BLUE))
    story.append(d)

class NumberedCanvas(canvas.Canvas):
    def __init__(self,*a,**kw):super().__init__(*a,**kw);self.pages=[]
    def showPage(self):self.pages.append(dict(self.__dict__));self._startPage()
    def save(self):
        total=len(self.pages)
        for state in self.pages:
            self.__dict__.update(state)
            self.setFont('Times-Italic',8);self.setFillColor(GRAY)
            self.drawString(48,A4[1]-31,'Department of AIML')
            self.drawRightString(A4[0]-48,A4[1]-31,'Advance NLP (AML23702)')
            self.setStrokeColor(colors.HexColor('#b6b6b6'));self.setLineWidth(.4)
            self.line(48,A4[1]-38,A4[0]-48,A4[1]-38)
            self.setFont('Times-Roman',8)
            self.drawCentredString(A4[0]/2,25,f'Page {self._pageNumber} of {total}')
            super().showPage()
        super().save()
