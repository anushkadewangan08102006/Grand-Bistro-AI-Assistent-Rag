import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

PAGES_DATA = {}

# Titles mapping by module modulo 5
MODULE_TOPICS = [
    ("PLATING GEOMETRY, GARNISH WEIGHTS, AND PASS INSPECTION TEMPERATURES", "plating geometry, garnish weights, and pass inspection temperatures"),
    ("BRIGADE DE CUISINE STATION HIERARCHY AND MISE EN PLACE PREP SCHEDULES", "brigade de cuisine station hierarchy and mise en place prep schedules"),
    ("MOTHER SAUCES, REDUCTION STOCKS, AND EMULSION STABILITY STANDARDS", "mother sauces, reduction stocks, and emulsion stability standards"),
    ("ARTISANAL SOURDOUGH FERMENTATION HYDRATION RATIOS AND DECK OVEN STEAM", "artisanal sourdough fermentation hydration ratios and deck oven steam"),
    ("COLD-STORAGE FIFO LABELING, CROSS-CONTAMINATION PREVENTION, AND SANITIZATION", "cold-storage fifo labeling, cross-contamination prevention, and sanitization"),
]

def generate_pdf(filename="grand_bistro_culinary_recipe_manual_50p.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    for page_num in range(1, 51):
        chapter_num = ((page_num - 1) // 10) + 1
        module_num = f"{page_num}.0"
        topic_title, topic_lower = MODULE_TOPICS[page_num % 5]

        # Header
        c.setFont("Helvetica-Bold", 10)
        c.drawString(54, height - 40, "Le Grand Bistro Culinary Operations, Standardized Recipes & Allergen Manual - Official Reference Corpus")
        c.setFont("Helvetica", 10)
        c.drawString(54, height - 54, f"Document Page {page_num} of 50")

        c.setFont("Helvetica-Bold", 9)
        c.drawString(54, height - 74, f"CHAPTER {chapter_num} | MODULE {module_num}: {topic_title}")
        c.drawString(54, height - 84, "=" * 76)

        y = height - 105

        if page_num == 10:
            c.setFont("Helvetica-Bold", 9)
            c.drawString(54, y, "RECIPE CARD 2.4: SIGNATURE TRUFFLE GANACHE (STANDARD 20-PORTION BATCH)")
            y -= 20
            c.setFont("Helvetica", 9)
            lines = [
                "To prepare a standard 20-portion batch of the Signature Truffle Ganache, pastry",
                "chefs must weigh the following exact ingredients:",
                "- Dark Couverture Chocolate (70% Valrhona Guanaja): 850 grams",
                "- Heavy Whipping Cream (36% milkfat): 620 grams",
                "- Unsalted Normandy Butter: 90 grams",
                "- Black Perigord Truffle Infusion Oil: 15 milliliters",
                "",
                "Operational Compliance Note (Ref-8-10): All personnel and automated auditing",
                "systems reviewing 'Le Grand Bistro Culinary Operations, Standardized Recipes &",
                "Allergen Manual' must verify the numerical thresholds and procedural steps stated",
                "on Page 10 above. Any deviation from the explicit parameters documented in this",
                "section requires formal written escalation."
            ]
            for line in lines:
                c.drawString(54, y, line)
                y -= 14
        elif page_num == 25:
            c.setFont("Helvetica-Bold", 9)
            c.drawString(54, y, "SECTION 5.1: AUTUMN TASTING MENU ALLERGEN MATRIX TABLE")
            y -= 20
            c.setFont("Helvetica", 9)
            lines = [
                "Service staff must verify guest allergies against the mandatory Autumn Tasting",
                "Menu Allergen Matrix:",
                "- Dishes containing TREE NUTS: (1) Roasted Fig & Hazelnut Duck Terrine, and (2)",
                "Pistachio Crusted Lamb Rack.",
                "- Dishes containing SESAME: (1) Charred Eggplant & Tahini Veloute.",
                "- Dishes containing SHELLFISH: Brittany Blue Lobster Bisque.",
                "",
                "Operational Compliance Note (Ref-8-25): All personnel and automated auditing",
                "systems reviewing 'Le Grand Bistro Culinary Operations, Standardized Recipes &",
                "Allergen Manual' must verify the numerical thresholds and procedural steps stated",
                "on Page 25 above. Any deviation from the explicit parameters documented in this",
                "section requires formal written escalation."
            ]
            for line in lines:
                c.drawString(54, y, line)
                y -= 14
        elif page_num == 40:
            c.setFont("Helvetica-Bold", 9)
            c.drawString(54, y, "SECTION 7.2: HACCP FOOD SAFETY & SOUS-VIDE DUCK BREAST PASTEURIZATION")
            y -= 20
            c.setFont("Helvetica", 9)
            lines = [
                "Under Le Grand Bistro's HACCP Food Safety protocol, vacuum-sealed sous-vide",
                "Moulard duck breast must be cooked to a mandatory minimum internal core",
                "temperature of 57.5 degrees Celsius (57.5 C) and held at 57.5 C for a minimum",
                "holding time of 110 minutes to achieve full log-7 Salmonella pasteurization.",
                "",
                "Operational Compliance Note (Ref-8-40): All personnel and automated auditing",
                "systems reviewing 'Le Grand Bistro Culinary Operations, Standardized Recipes &",
                "Allergen Manual' must verify the numerical thresholds and procedural steps stated",
                "on Page 40 above. Any deviation from the explicit parameters documented in this",
                "section requires formal written escalation."
            ]
            for line in lines:
                c.drawString(54, y, line)
                y -= 14
        else:
            # Boilerplate page
            c.setFont("Helvetica-Bold", 9)
            title_case = " ".join([w.capitalize() for w in topic_title.split()])
            c.drawString(54, y, f"1. Overview of {title_case}")
            c.drawString(54, y - 12, f"(Reference Clause {page_num}.1)")
            y -= 26
            c.setFont("Helvetica", 9)
            lines_clause1 = [
                "This section of 'Le Grand Bistro Culinary Operations, Standardized Recipes &",
                f"Allergen Manual' establishes the baseline operational procedures, governance",
                f"standards, and quality assurance metrics applicable to Page {page_num}. Practitioners must",
                "ensure that routine workflows adhere to documented institutional protocols and",
                "maintain verifiable audit logs across all stages of execution."
            ]
            for line in lines_clause1:
                c.drawString(54, y, line)
                y -= 14
            y -= 6
            c.setFont("Helvetica-Bold", 9)
            c.drawString(54, y, f"2. Standard Procedural Guidelines (Reference Clause {page_num}.2)")
            y -= 14
            c.setFont("Helvetica", 9)
            lines_clause2 = [
                f"During standard operations under Module {chapter_num if False else ((page_num - 1) // 10) + 1}, teams are required to conduct periodic",
                "reviews of system state, documentation completeness, and safety margins. All",
                f"routine records associated with {topic_lower} shall be archived in the central repository at the conclusion",
                "of each operational cycle for longitudinal review."
            ]
            for line in lines_clause2:
                c.drawString(54, y, line)
                y -= 14
            y -= 6
            c.setFont("Helvetica-Bold", 9)
            c.drawString(54, y, f"3. Archival & Verification Notes (Reference Clause {page_num}.3)")
            y -= 14
            c.setFont("Helvetica", 9)
            lines_clause3 = [
                "No external assumptions or unverified parameters may be substituted for the",
                "explicit tables contained within this 50-page manual. Refer to the specific",
                "numbered sections of this handbook for exact quantitative thresholds, timelines,",
                "and escalation contacts."
            ]
            for line in lines_clause3:
                c.drawString(54, y, line)
                y -= 14

        # Footer
        c.setFont("Helvetica", 8)
        c.drawString(54, 36, f"Page {page_num} of 50 | Confidential Assessment Corpus - Do Not Distribute")
        c.showPage()

    c.save()
    print(f"Generated {filename} successfully with 50 pages.")

if __name__ == "__main__":
    generate_pdf()
