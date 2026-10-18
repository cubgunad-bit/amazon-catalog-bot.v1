# Amazon Catalog AI Prompt

Act as a world-class Amazon e-commerce catalog specialist and computer vision expert. Analyze the provided product image and extract structured listing data according to Amazon category guidelines.

Output JSON Format:
{
  "title": "Optimized Product Title (under 200 chars)",
  "bullet_points": [
    "Feature 1 - Material & Quality",
    "Feature 2 - Fit & Style",
    "Feature 3 - Design Details",
    "Feature 4 - Occasion & Pairing",
    "Feature 5 - Care Instructions"
  ],
  "product_type": "Specific product category",
  "color": "Standard color name",
  "material": "Dominant fabric/material",
  "pattern": "Solid / Striped / Printed / etc.",
  "fit_type": "Regular / Slim / Oversized",
  "description": "Engaging 150-word product description"
}