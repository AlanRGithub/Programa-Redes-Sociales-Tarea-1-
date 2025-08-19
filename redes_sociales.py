import pandas as pd
import re

def cargar(path="datos_redes_sociales.csv"):
    df = pd.read_csv(path)
    df.columns = [c.strip().upper() for c in df.columns]
    if 'RED SOCIAL' in df.columns:
        df['RED SOCIAL'] = df['RED SOCIAL'].astype(str).str.strip().str.upper()
    if 'CONCEPTO' in df.columns:
        df['CONCEPTO'] = df['CONCEPTO'].astype(str).str.strip().str.upper()
    return df

def valor_num(row, month):
    if month not in row:
        return None
    v = row.get(month)
    if pd.isna(v):
        return None
    s = str(v).strip()
    if s == '':
        return None
    is_percent = '%' in s
    s = s.replace('%','').replace('(', '').replace(')', '').replace(' ', '')
    s = re.sub(r'[^0-9\.,\-]', '', s)
    if s == '' or s == '-' or s == '--':
        return None

    if '.' in s and ',' in s:
        if s.rfind(',') > s.rfind('.'):
            s = s.replace('.', '').replace(',', '.')
        else:
            s = s.replace(',', '')
    elif ',' in s and '.' not in s:
        parts = s.split(',')
        if len(parts) > 1 and len(parts[-1]) == 3:
            s = ''.join(parts)
        else:
            s = s.replace(',', '.')
    else:
        pass

    s = s.strip()
    try:
        val = float(s)
        return val
    except Exception:
        return None

MONTHS = ['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']

def encontrar_fila(df, red, concepto_substr):
    mask = (df['RED SOCIAL']==red) & (df['CONCEPTO'].str.contains(concepto_substr))
    if not mask.any():
        return None
    return df.loc[mask].iloc[0]

def diferencia_followers_twitter(df):
    row = encontrar_fila(df, 'TWITTER', 'SEGUIDORES')
    if row is None:
        return None, None, None
    ene = valor_num(row, 'ENERO')
    jun = valor_num(row, 'JUNIO')
    diff = None
    if ene is not None and jun is not None:
        diff = jun - ene
    return ene, jun, diff

def diferencia_visualizaciones_yt(df, m1, m2):
    m1u = m1.strip().upper(); m2u = m2.strip().upper()
    if m1u not in MONTHS or m2u not in MONTHS:
        raise ValueError("Mes inválido. Ejemplo: enero, junio")
    row = encontrar_fila(df, 'YOUTUBE', 'VISUALIZACIONES')
    if row is None:
        return m1u, None, m2u, None, None
    v1 = valor_num(row, m1u)
    v2 = valor_num(row, m2u)
    diff = None
    if v1 is not None and v2 is not None:
        diff = v2 - v1
    return m1u, v1, m2u, v2, diff

def promedio_crecimiento(df, platform):
    platform = platform.strip().upper()
    if platform not in ('TWITTER','FACEBOOK'):
        return None
    row = encontrar_fila(df, platform, 'CRECIMIENTO')
    if row is None:
        return None
    vals = []
    for m in MONTHS[:6]:
        v = valor_num(row, m)
        if v is not None:
            vals.append(v)
    return (sum(vals)/len(vals)) if vals else None

def promedio_megusta_plataformas(df):
    results = {}
    for name in ['FACEBOOK','TWITTER','YOUTUBE']:
        row = encontrar_fila(df, name, 'ME GUSTA')
        if row is None:
            results[name] = None
            continue
        vals = []
        for m in MONTHS[:6]:
            v = valor_num(row, m)
            if v is not None:
                vals.append(v)
        results[name] = (sum(vals)/len(vals)) if vals else None
    return results

def fmt(x):
    if x is None:
        return "N/A"
    if isinstance(x, float) and x.is_integer():
        return f"{int(x):,}"
    if isinstance(x, float):
        return f"{x:,.2f}"
    return str(x)

def main():
    df = cargar('datos_redes_sociales.csv')
    print("Archivo cargado. Resumen rápido:")
    print(df.head(8).to_string(index=False))
    print("\n1) Diferencia followers en Twitter entre ENERO y JUNIO:")
    ene, jun, diff = diferencia_followers_twitter(df)
    print(f"   Enero: {fmt(ene)}, Junio: {fmt(jun)}, Diferencia (Jun - Ene): {fmt(diff)}")
    print("\n2) Diferencia de visualizaciones en YouTube entre meses seleccionados:")
    m1 = input('   Escribe el primer mes (ej. enero): ')
    m2 = input('   Escribe el segundo mes (ej. junio): ')
    try:
        m1u, v1, m2u, v2, diffv = diferencia_visualizaciones_yt(df, m1, m2)
        print(f"   {m1u}: {fmt(v1)}, {m2u}: {fmt(v2)}, Diferencia ({m2u} - {m1u}): {fmt(diffv)}")
    except Exception as e:
        print('   Error:', e)
    print("\n3) Promedio de crecimiento de TWITTER y FACEBOOK (ENERO-JUNIO):")
    p_tw = promedio_crecimiento(df, 'TWITTER')
    p_fb = promedio_crecimiento(df, 'FACEBOOK')
    print(f"   Twitter (promedio crecimiento): {fmt(p_tw)}")
    print(f"   Facebook (promedio crecimiento): {fmt(p_fb)}")
    print("\n4) Promedio de 'Me gusta' (ENERO-JUNIO) por plataforma:")
    likes = promedio_megusta_plataformas(df)
    for k,v in likes.items():
        print(f"   {k}: {fmt(v)}")
    print("\nFin del programa.")

if __name__=='__main__':
    main()
