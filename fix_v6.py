import re

content = open('p2c_v6.html', 'r', encoding='utf-8').read()

# 1. Fix case sensitivity in login
content = content.replace(
    "email=eq.${encodeURIComponent(email)}",
    "email=ilike.${encodeURIComponent(email)}"
)

# 2. Add esc function and toast CSS/JS
esc_code = """
/* ── TOAST ── */
#toastWrap {position:fixed;bottom:20px;right:20px;z-index:9999;display:flex;flex-direction:column;gap:10px;pointer-events:none}
.toast {min-width:250px;padding:12px 16px;border-radius:8px;font-size:13px;font-weight:600;color:#fff;box-shadow:0 4px 12px rgba(0,0,0,0.15);animation:t-in 0.3s forwards}
@keyframes t-in {from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
.toast.success {background:#2e7d32}
.toast.error {background:#d32f2f}
.toast.info {background:#1565c0}
"""
content = content.replace("</style>", esc_code + "</style>")
content = content.replace("<body>", "<body>\n<div id=\"toastWrap\"></div>")

toast_js = """
function esc(str) {
  if (str === null || str === undefined) return '';
  return String(str).replace(/[&<>"']/g, function(m) {
    return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[m];
  });
}

function showToast(msg, type='info') {
  const wrap = document.getElementById('toastWrap');
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.textContent = msg;
  wrap.appendChild(t);
  setTimeout(() => {
    t.style.opacity = '0';
    t.style.transition = 'opacity 0.3s';
    setTimeout(() => t.remove(), 300);
  }, 3000);
}
"""
content = content.replace("/* ── LİSTELER ── */", toast_js + "\n/* ── LİSTELER ── */")

# 3. Replace alert with showToast where applicable
content = content.replace("alert('Hata: '+e.message);", "showToast('Hata: '+e.message, 'error');")
content = content.replace("alert('Kaydedildi!');", "showToast('Kaydedildi!', 'success');")
content = content.replace("alert('Güncellendi!');", "showToast('Güncellendi!', 'success');")
content = content.replace("alert('Silindi!');", "showToast('Silindi!', 'success');")

# 4. Apply esc() to string outputs
vars_to_escape = [
  't.tn', 't.musteri_adi', 't.musteri_yetkilisi', 't.fatura_adresi', 't.sevk_adresi', 't.is_tanimi', 't.teknik_satis_muh', 't.teklifi_hazirlayan', 't.ic_onay_yapan',
  'proj.pn', 'proj.tn', 'proj.musteri_adi', 'proj.musteri_yetkilisi', 'proj.fatura_adresi', 'proj.sevk_adresi', 'proj.is_tanimi', 'proj.teknik_satis_muh', 'proj.genel_durum', 'proj.is_emri_no',
  'x.pn', 'x.tn', 'x.musteri_adi', 'x.is_tanimi', 'x.teknik_satis_muh', 'x.aciklama', 'prj.musteri_adi',
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

# Optimistic Updates in api()
api_old = '''async function api(table,params='',method='GET',body=null){
  const h={'apikey':KEY,'Authorization':'Bearer '+authToken,'Content-Type':'application/json'};
  if(method==='POST'||method==='PATCH') h['Prefer']='return=representation';
  const r=await fetch(`${SB}/rest/v1/${table}?${params}`,{method,headers:h,body:body?JSON.stringify(body):null});
  if(!r.ok) throw new Error(await r.text());
  const t=await r.text(); return t?JSON.parse(t):[];
}'''
api_new = '''async function api(table,params='',method='GET',body=null){
  const h={'apikey':KEY,'Authorization':'Bearer '+authToken,'Content-Type':'application/json'};
  if(method==='POST'||method==='PATCH') h['Prefer']='return=representation';
  const r=await fetch(`${SB}/rest/v1/${table}?${params}`,{method,headers:h,body:body?JSON.stringify(body):null});
  if(!r.ok) {
    const txt = await r.text();
    let msg = txt;
    try { msg = JSON.parse(txt).message || txt; } catch(e){}
    throw new Error(msg);
  }
  
  if(method==='DELETE') {
    if (params.includes('eq.') && db[table]) {
      const parts = params.split('=eq.');
      if(parts.length === 2) {
        const col = parts[0];
        const val = parts[1].replace(/"/g, '');
        db[table] = db[table].filter(x => String(x[col]) !== String(val));
      }
    }
    return true;
  }
  
  const t=await r.text(); 
  const res = t ? JSON.parse(t) : [];
  
  if((method==='POST'||method==='PATCH') && res.length && db[table]){
    res.forEach(item => {
      const idCol = item.id ? 'id' : (item.pn ? 'pn' : null);
      if(idCol) {
        if(method==='POST') {
          db[table].unshift(item);
        } else {
          const idx = db[table].findIndex(x => String(x[idCol]) === String(item[idCol]));
          if(idx > -1) db[table][idx] = item;
        }
      }
    });
  }
  return res;
}'''
content = content.replace(api_old, api_new)

# Optimize loadAll to use Promise.all
loadAll_old = '''async function loadAll(){
  setSS('Yükleniyor...');
  try{
    db.teklifler=await api('teklifler','select=*&order=created_at.desc');
    db.projeler=await api('projeler','select=*&order=created_at.desc');
    db.kalemler=await api('kalemler','select=*&order=pn.asc,kalem_sira.asc');
    setSS(''); buildNav(); renderTab(currentTab);
  }catch(e){setSS('Hata: '+e.message);}
}'''
loadAll_new = '''async function loadAll(){
  setSS('Yükleniyor...');
  try{
    const [t,p,k]=await Promise.all([
      api('teklifler','select=*&order=created_at.desc'),
      api('projeler','select=*&order=created_at.desc'),
      api('kalemler','select=*&order=pn.asc,kalem_sira.asc')
    ]);
    db={teklifler:t,projeler:p,kalemler:k};
    setSS(''); buildNav(); renderTab(currentTab);
  }catch(e){setSS('Hata: '+e.message);}
}'''
content = content.replace(loadAll_old, loadAll_new)

# Eliminate await loadAll() calls that were over-fetching
content = content.replace("await loadAll(); showTab('teklifler');", "buildNav(); renderTab(currentTab); showTab('teklifler');")
content = content.replace("await loadAll(); showTab('projeler');", "buildNav(); renderTab(currentTab); showTab('projeler');")
content = content.replace("await loadAll();closeM();", "buildNav(); renderTab(currentTab); closeM();")

open('p2c_v6.html', 'w', encoding='utf-8').write(content)
