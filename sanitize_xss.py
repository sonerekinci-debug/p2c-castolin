import re

with open('p2c_v6.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Update sb() and catb() functions
sb_orig = r"function sb\(s\)\{[\s\S]*?return `<span class=\"badge b-gray\">\$\{s\}</span>`;\n\}"
sb_new = """function sb(s){
  if(!s) return '<span class=\"badge b-gray\">—</span>';
  const orig = s;
  s = esc(s);
  if(['ONAYLANDI','Tamamlandı','Eklendi','Onaylandı'].includes(orig)) return `<span class=\"badge b-green\">${s}</span>`;
  if(['ONAY BEKLİYOR','DEĞERLENDİRMEDE','Çalışılıyor'].includes(orig)) return `<span class=\"badge b-amber\">${s}</span>`;
  if(orig.startsWith('OLUMSUZ')||orig==='Reddedildi') return `<span class=\"badge b-red\">${orig.length>20?esc(orig.substring(0,20))+'…':s}</span>`;
  if(['ÜRETİME SEVKEDİLDİ','Üretimde','QC BEKLİYOR','FATURA BEKLİYOR','SEVKİYAT BEKLİYOR'].includes(orig)) return `<span class=\"badge b-blue\">${s}</span>`;
  if(['PROJE KODU EKLENMELİ','TEKNİK ŞARTNAME BEKLİYOR','ÜRETİM BEKLİYOR'].includes(orig)) return `<span class=\"badge b-orange\">${s}</span>`;
  return `<span class=\"badge b-gray\">${s}</span>`;
}"""
content = re.sub(sb_orig, sb_new, content)

catb_orig = r"function catb\(k\)\{[\s\S]*?return `<span class=\"badge b-gray\" title=\"\$\{k\}\">\$\{s\}</span>`;\n\}"
catb_new = """function catb(k){
  if(!k) return '<span class=\"badge b-gray\">—</span>';
  const orig = k;
  const s=esc(orig.length>14?orig.substring(0,14)+'…':orig);
  const ek = esc(orig);
  if(orig.includes('Cut')||orig.includes('LaserClad')||orig.includes('VRM')) return `<span class=\"badge b-blue\" title=\"${ek}\">${s}</span>`;
  if(orig.includes('Welding')||orig.includes('Boiler')) return `<span class=\"badge b-amber\" title=\"${ek}\">${s}</span>`;
  if(orig.includes('Coating')||orig.includes('Carrier')) return `<span class=\"badge b-teal\" title=\"${ek}\">${s}</span>`;
  return `<span class=\"badge b-gray\" title=\"${ek}\">${s}</span>`;
}"""
content = re.sub(catb_orig, catb_new, content)

vars_to_escape = [
  't.tn', 't.musteri_adi', 't.musteri_yetkilisi', 't.fatura_adresi', 't.sevk_adresi', 't.is_tanimi', 't.teknik_satis_muh', 't.teklifi_hazirlayan', 't.ic_onay_yapan',
  'proj.pn', 'proj.tn', 'proj.musteri_adi', 'proj.musteri_yetkilisi', 'proj.fatura_adresi', 'proj.sevk_adresi', 'proj.is_tanimi', 'proj.teknik_satis_muh', 'proj.genel_durum', 'proj.is_emri_no',
  'x.pn', 'x.tn', 'x.musteri_adi', 'x.is_tanimi', 'x.teknik_satis_muh',
  'k.aciklama', 'k.qc_rapor_no', 'k.fatura_no', 'k.sevkiyat_bilgisi',
  'a.desc', 'a.no', 'a.eksik',
  'r.s', 'r.tn', 'r.musteri', 'r.hazirlayan'
]

def replacer(match):
    inner = match.group(1)
    if inner.startswith('esc(') or inner.startswith('sb(') or inner.startswith('catb('):
        return match.group(0)
    
    core_var = inner.split('||')[0].strip() if '||' in inner else inner.strip()
    if core_var in vars_to_escape:
        return f"${{esc({inner})}}"
    return match.group(0)

content = re.sub(r'\$\{([^}]+)\}', replacer, content)

with open('p2c_v6.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Sanitized successfully.")
