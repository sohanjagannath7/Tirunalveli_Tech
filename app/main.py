from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.data import PAGES, SERVICES, SITE_NAME, SPARE_PARTS_CATEGORIES

app = FastAPI(title=SITE_NAME, docs_url=None, redoc_url=None)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("simple_page.html", {"request": request, "page": PAGES["home"]})

@app.get("/about", response_class=HTMLResponse)
async def read_about(request: Request):
    return templates.TemplateResponse("simple_page.html", {"request": request, "page": PAGES["about"]})

@app.get("/contact", response_class=HTMLResponse)
async def read_contact(request: Request):
    return templates.TemplateResponse("simple_page.html", {"request": request, "page": PAGES["contact"]})

@app.get("/spare-parts/tirunelveli", response_class=HTMLResponse)
async def read_spare_parts(request: Request):
    return templates.TemplateResponse("spare_parts.html", {
        "request": request, 
        "page": PAGES["spare_parts"],
        "categories": SPARE_PARTS_CATEGORIES
    })

@app.get("/spare-parts/{category_slug}", response_class=HTMLResponse)
async def read_spare_parts_category(request: Request, category_slug: str):
    if category_slug not in SPARE_PARTS_CATEGORIES:
         # If not a category, it might be the hub (technically handled by exact match above, but safe fallback logic or 404)
        if category_slug == "tirunelveli":
             return await read_spare_parts(request)
        raise HTTPException(status_code=404, detail="Category not found")
    
    return templates.TemplateResponse("spare_parts_category.html", {
        "request": request, 
        "category": SPARE_PARTS_CATEGORIES[category_slug]
    })

@app.get("/technicians", response_class=HTMLResponse)
async def read_technicians_hub(request: Request):
    return templates.TemplateResponse("technicians_hub.html", {
        "request": request, 
        "page": PAGES["technicians_hub"],
        "services": SERVICES
    })

@app.get("/technicians/{service_slug}", response_class=HTMLResponse)
async def read_service_page(request: Request, service_slug: str):
    if service_slug not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")
    
    return templates.TemplateResponse("service_page.html", {
        "request": request, 
        "service": SERVICES[service_slug]
    })

@app.get("/sitemap.xml", response_class=PlainTextResponse)
async def sitemap(request: Request):
    base_url = str(request.base_url).rstrip("/")
    # Hardcoded routes
    routes = [
        "/",
        "/about",
        "/contact",
        "/technicians",
        "/spare-parts/tirunelveli"
    ]
    # Dynamic routes
    for slug in SERVICES:
        routes.append(f"/technicians/{slug}")
    for slug in SPARE_PARTS_CATEGORIES:
        routes.append(f"/spare-parts/{slug}")
    
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for route in routes:
        xml += '  <url>\n'
        xml += f'    <loc>{base_url}{route}</loc>\n'
        xml += '    <changefreq>weekly</changefreq>\n'
        xml += '  </url>\n'
        
    xml += '</urlset>'
    return HTMLResponse(content=xml, media_type="application/xml")
