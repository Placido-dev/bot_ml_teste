from playwright.sync_api import sync_playwright
import json

def buscar_ofertas_ml(desconto_minimo=20):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        page.goto("https://www.mercadolivre.com.br/ofertas#nav-header", timeout=60000)
        page.wait_for_load_state("networkidle", timeout=30000)
        page.evaluate("window.scrollTo(0, 1000)")
        page.wait_for_timeout(2000)

        # DOM do JS

        dados = page.evaluate("""
            () => {
                const cards = document.querySelectorAll('[class*="poly-card"], [class*="poly-component"]');
                return Array.from(cards).map(card => {
                    const titulo_el = card.querySelector('.poly-component__title');
                    const fracao = card.querySelector('.poly-price__current .andes-money-amount__fraction');
                    const centavos = card.querySelector('.poly-price__current .andes-money-amount__cents');
                    const desconto_el = card.querySelector('.polylabel-pill');

                    const titulo = titulo_el ? titulo_el.innerText.trim() : null;
                    const href = titulo_el ? titulo_el.href : null;
                    const preco_atual = fracao ? parseFloat(fracao.innerText.replace('.', '') + '.' + (centavos ? centavos.innerText : '00')) : null;
                    const desconto_txt = desconto_el ? desconto_el.innerText.trim() : null;
                    const desconto_pct = desconto_txt ? parseFloat(desconto_txt.replace('% OFF', '')) : null;

                    return { titulo, href, preco_atual, desconto_pct };
                }).filter(d => d.titulo && d.preco_atual);
            }
        """)

        browser.close()

    # remove duplicados e formatção
    vistos = set()
    unicos = []
    for d in dados:
        if d['titulo'] not in vistos and d['desconto_pct'] and d['desconto_pct'] >= desconto_minimo:
            vistos.add(d['titulo'])
            unicos.append(d)

    return unicos

def formatar_whatsapp(promocoes):
    linhas = ["🔥 *PROMOÇÕES DO DIA - MERCADO LIVRE - CHAMA RESPEITA TA BRINCANDO* 🔥\n"]
    for p in promocoes:
        linha = (
            f"✅ *{p['titulo'][:60]}*\n"
            f"💰 R$ {p['preco_atual']:.2f} ({p['desconto_pct']:.0f}% OFF)\n"
            f"🔗 {p['href'].split('#')[0]}\n"
        )
        linhas.append(linha)
    return "\n".join(linhas)

if __name__ == "__main__":
    promocoes = buscar_ofertas_ml(desconto_minimo=30)
    print(f"{len(promocoes)} promoções encontradas\n")
    print(formatar_whatsapp(promocoes))