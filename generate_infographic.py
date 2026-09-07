#!/usr/bin/env python3
"""
generate_infographic.py

Generates a thesis-tailored publication-grade SVG and high-resolution PNG
depicting successful orbital space launches from 1957 through September 2026.

Specifications:
- Pure white background (#ffffff) for seamless LaTeX integration.
- Aspect ratio slightly wider than A4 vertical (Width: 1900px, Height: 2280px, ~1:1.20).
- Starts directly with the graphic (no title banner, deck, red ribbon, or publisher names).
- Uniform, larger year typography in the center spine for all 70 years.
- Grouped rectangular blocks per provider with identical 2.2px gaps horizontally and vertically.
- Only successful launches included (no failures, no hatch patterns).
- No 2018 cutoff line or badge.
- Larger, crisp font sizes throughout.
- Generous clearance for all annotations to prevent any overlap with colored bars or adjacent labels.
"""

import os
import json
import subprocess

DATA_JSON = '/home/dcas/g.pelenghi/Documents/antigravity/infographic/data/launches_grouped.json'
OUTPUT_SVG = '/home/dcas/g.pelenghi/Documents/antigravity/infographic/infographic_space_launches_2026.svg'
OUTPUT_PNG = '/home/dcas/g.pelenghi/Documents/antigravity/infographic/infographic_space_launches_2026.png'

# Color mappings
COLORS = {
    # Private / Commercial
    'SpaceX': '#c82274',
    'Arianespace': '#f26522',
    'ULA': '#2b7bba',
    'Rocket Lab': '#009e73',
    'China Commercial': '#d99b00',
    'US Heritage Commercial': '#1e4b7a',
    'International Commercial': '#75588a',
    'US New Commercial': '#2ca25f',
    'Other Commercial': '#7d8c99',
    
    # Sovereign State
    'USSR': '#d12b2b',
    'Russia': '#8a4f9e',
    'United States': '#1a689e',
    'China': '#2e8540',
    'India': '#e65100',
    'Japan': '#00a2d4',
    'Europe': '#59a14f',
    'Other States': '#78828c',
}

def build_svg():
    with open(DATA_JSON, 'r', encoding='utf-8') as f:
        yearly_data = json.load(f)
        
    # Dimensions: Vertical, slightly wider than A4 (1900 x 2280 -> 1 : 1.20)
    width = 1900
    height = 2280
    
    # Center spine coordinates
    center_x = 1040
    spine_half_width = 30
    x_private_start = center_x - spine_half_width
    x_state_start = center_x + spine_half_width
    
    # Modular bar geometry
    # Gap between providers horizontally = gap between rows vertically
    provider_gap = 2.2
    row_gap = 2.2
    bar_height = 24.0
    row_step = bar_height + row_gap # 26.2 px
    bar_y_offset = -bar_height / 2.0
    unit_w = 3.65 # pixels per successful launch
    
    top_y = 130
    years_count = len(yearly_data) # 70 years (1957 to 2026)
    bottom_y = top_y + (years_count - 1) * row_step # 1937.8 px
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    
    # Styles & Fonts
    svg.append('<defs>')
    svg.append('''
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@400;500;600;700&amp;display=swap');
            
            text {
                font-family: "Liberation Sans", "DejaVu Sans", "Libre Franklin", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }
            .heading {
                font-family: "Liberation Sans", "DejaVu Sans", "Libre Franklin", sans-serif;
                font-weight: 700;
                letter-spacing: 0.8px;
            }
        </style>
    ''')
    svg.append('</defs>')
    
    # Pure White Background
    svg.append(f'<rect width="{width}" height="{height}" fill="#ffffff"/>')
    
    # -------------------------------------------------------------
    # TOP HEADER SECTION (Starts directly with graph, thesis-tailored)
    # -------------------------------------------------------------
    
    # Left: Commercial / Private
    svg.append(f'<text x="{center_x - 140}" y="52" font-size="24" font-weight="700" fill="#111111" text-anchor="end" class="heading">COMMERCIAL / PRIVATE OPERATORS</text>')
    svg.append(f'<text x="{center_x - 140}" y="75" font-size="14" font-weight="500" fill="#555555" text-anchor="end">← Grouped by company (SpaceX, Arianespace, ULA, Rocket Lab, Chinese startups)</text>')
    
    # Scale ticks Commercial side (Leftwards from center)
    scale_y = 90
    for tick in [50, 100, 150, 200]:
        tick_x = x_private_start - tick * unit_w
        svg.append(f'<line x1="{tick_x:.1f}" y1="{top_y - 20}" x2="{tick_x:.1f}" y2="{bottom_y + 16}" stroke="#e8e8e8" stroke-width="1" stroke-dasharray="3,3"/>')
        svg.append(f'<text x="{tick_x:.1f}" y="{top_y - 26}" font-size="13" font-weight="600" fill="#777777" text-anchor="middle">{tick}</text>')
        
    # Scale ticks Sovereign State side (Rightwards from center)
    for tick in [50, 100]:
        tick_x = x_state_start + tick * unit_w
        svg.append(f'<line x1="{tick_x:.1f}" y1="{top_y - 20}" x2="{tick_x:.1f}" y2="{bottom_y + 16}" stroke="#e8e8e8" stroke-width="1" stroke-dasharray="3,3"/>')
        svg.append(f'<text x="{tick_x:.1f}" y="{top_y - 26}" font-size="13" font-weight="600" fill="#777777" text-anchor="middle">{tick}</text>')
    
    # Center: Year Spine Header
    svg.append(f'<text x="{center_x}" y="62" font-size="16" font-weight="700" fill="#333333" text-anchor="middle" letter-spacing="1.2">YEAR</text>')
    
    # Right: Sovereign State
    svg.append(f'<text x="{center_x + 140}" y="52" font-size="24" font-weight="700" fill="#111111" text-anchor="start" class="heading">SOVEREIGN STATE AGENCIES</text>')
    svg.append(f'<text x="{center_x + 140}" y="75" font-size="14" font-weight="500" fill="#555555" text-anchor="start">Grouped by nation / agency (USSR, United States, Russia, China, India, Japan, ESA) →</text>')
    
    # Header divider line
    svg.append(f'<line x1="60" y1="96" x2="{width - 60}" y2="96" stroke="#d5d5d5" stroke-width="1.2"/>')
    
    # Center spine guide lines and subtle shading
    svg.append(f'<rect x="{center_x - spine_half_width}" y="{top_y - 14}" width="{spine_half_width*2}" height="{bottom_y - top_y + 28}" fill="#f6f6f5" opacity="0.9"/>')
    svg.append(f'<line x1="{center_x - spine_half_width}" y1="{top_y - 14}" x2="{center_x - spine_half_width}" y2="{bottom_y + 14}" stroke="#d0d0ce" stroke-width="1"/>')
    svg.append(f'<line x1="{center_x + spine_half_width}" y1="{top_y - 14}" x2="{center_x + spine_half_width}" y2="{bottom_y + 14}" stroke="#d0d0ce" stroke-width="1"/>')
    
    # Render Rows (1957 to 2026)
    for idx, row in enumerate(yearly_data):
        year = row['year']
        y_curr = top_y + idx * row_step
        
        # Row guide line
        svg.append(f'<line x1="60" y1="{y_curr:.2f}" x2="{width - 60}" y2="{y_curr:.2f}" stroke="#f2f2f2" stroke-width="0.75"/>')
        
        # Uniform Year Label (same weight and larger size for all 70 years)
        year_str = f"{year}*" if year == 2026 else str(year)
        svg.append(f'<text x="{center_x}" y="{y_curr + 5.0:.2f}" font-size="14.5" font-weight="600" fill="#2c2c2c" text-anchor="middle">{year_str}</text>')
        
        # 1. RENDER PRIVATE BLOCKS (Leftwards, Successful Launches Only)
        curr_x_p = x_private_start
        for blk in row.get('private_blocks', []):
            prov = blk['provider']
            color = COLORS.get(prov, '#888888')
            succ_launches = [l for l in blk['launches'] if l['category'] == 'O']
            count = len(succ_launches)
            if count == 0:
                continue
                
            blk_w = count * unit_w
            blk_start_x = curr_x_p - blk_w
            
            for l_idx in range(count):
                tile_x = blk_start_x + l_idx * unit_w
                svg.append(f'<rect x="{tile_x:.2f}" y="{y_curr + bar_y_offset:.2f}" width="{unit_w:.2f}" height="{bar_height:.2f}" fill="{color}"/>')
                if l_idx > 0:
                    svg.append(f'<line x1="{tile_x:.2f}" y1="{y_curr + bar_y_offset:.2f}" x2="{tile_x:.2f}" y2="{y_curr + bar_y_offset + bar_height:.2f}" stroke="#ffffff" stroke-width="0.5" opacity="0.6"/>')
                    
            # Subtle boundary border around provider block
            svg.append(f'<rect x="{blk_start_x:.2f}" y="{y_curr + bar_y_offset:.2f}" width="{blk_w:.2f}" height="{bar_height:.2f}" fill="none" stroke="#222222" stroke-width="0.5" opacity="0.25"/>')
            curr_x_p = blk_start_x - provider_gap
            
        # 2. RENDER STATE BLOCKS (Rightwards, Successful Launches Only)
        curr_x_s = x_state_start
        for blk in row.get('state_blocks', []):
            prov = blk['provider']
            color = COLORS.get(prov, '#888888')
            succ_launches = [l for l in blk['launches'] if l['category'] == 'O']
            count = len(succ_launches)
            if count == 0:
                continue
                
            blk_w = count * unit_w
            blk_start_x = curr_x_s
            
            for l_idx in range(count):
                tile_x = blk_start_x + l_idx * unit_w
                svg.append(f'<rect x="{tile_x:.2f}" y="{y_curr + bar_y_offset:.2f}" width="{unit_w:.2f}" height="{bar_height:.2f}" fill="{color}"/>')
                if l_idx > 0:
                    svg.append(f'<line x1="{tile_x:.2f}" y1="{y_curr + bar_y_offset:.2f}" x2="{tile_x:.2f}" y2="{y_curr + bar_y_offset + bar_height:.2f}" stroke="#ffffff" stroke-width="0.5" opacity="0.6"/>')
                    
            svg.append(f'<rect x="{blk_start_x:.2f}" y="{y_curr + bar_y_offset:.2f}" width="{blk_w:.2f}" height="{bar_height:.2f}" fill="none" stroke="#222222" stroke-width="0.5" opacity="0.25"/>')
            curr_x_s = blk_start_x + blk_w + provider_gap

    # -------------------------------------------------------------
    # HISTORICAL ANNOTATIONS & MILESTONES (Zero overlaps, generous clearance)
    # -------------------------------------------------------------
    def draw_state_callout(year, title, desc1, desc2, bar_end_x, y_target=None):
        idx = year - 1957
        y_origin = top_y + idx * row_step
        y_text = y_target if y_target is not None else y_origin
        target_x = max(bar_end_x + 24, 1510)
        
        if y_target is not None and abs(y_target - y_origin) > 2:
            svg.append(f'<path d="M {bar_end_x:.1f} {y_origin:.1f} L {bar_end_x + 14:.1f} {y_origin:.1f} L {target_x - 12:.1f} {y_text:.1f}" stroke="#666666" stroke-width="1.1" fill="none"/>')
        else:
            svg.append(f'<path d="M {bar_end_x:.1f} {y_origin:.1f} L {target_x - 12:.1f} {y_origin:.1f}" stroke="#666666" stroke-width="1.1" fill="none"/>')
            
        svg.append(f'<circle cx="{bar_end_x:.1f}" cy="{y_origin:.1f}" r="2.5" fill="#333333"/>')
        svg.append(f'<text x="{target_x:.1f}" y="{y_text - 5:.1f}" font-size="15" font-weight="700" fill="#111111">{title}</text>')
        svg.append(f'<text x="{target_x:.1f}" y="{y_text + 12:.1f}" font-size="13" fill="#555555">{desc1}</text>')
        if desc2:
            svg.append(f'<text x="{target_x:.1f}" y="{y_text + 27:.1f}" font-size="13" fill="#555555">{desc2}</text>')

    # Right side historical annotations
    draw_state_callout(1957, "1957: Sputnik 1", "USSR opens Space Age with first artificial satellite", None, x_state_start + 8)
    draw_state_callout(1961, "1961: First Human in Space", "Vostok 1 orbits Earth carrying Yuri Gagarin", None, x_state_start + 78)
    draw_state_callout(1969, "1969: Apollo 11 Moon Landing", "NASA Saturn V lands first humans on lunar surface", None, x_state_start + 395)
    # Stagger 1970 downward so it does not collide with 1969 Apollo 11
    draw_state_callout(1970, "1970: Asian Space Programs", "China (Dongfanghong 1) & Japan (Osumi) reach orbit", None, x_state_start + 410, y_target=top_y + (1970 - 1957) * row_step + 26)
    draw_state_callout(1982, "1982: Peak Cold War Rate", "USSR achieves 106 successful launches in 1 year", None, x_state_start + 420)
    draw_state_callout(1991, "1991: Dissolution of the USSR", "Russian Federation assumes program; launch rates fall", None, x_state_start + 270)
    draw_state_callout(2003, "2003: Shenzhou 5", "China becomes 3rd nation with crewed spaceflight", None, x_state_start + 205)
    draw_state_callout(2022, "2020s: State Pivot to Deep Space", "NASA Artemis & CNSA Chang'e/Tiangong lunar focus;", "LEO satellite launches left to commercial sector", x_state_start + 310)

    # -------------------------------------------------------------
    # LEFT SIDE COMMERCIAL ANNOTATIONS (Perfect clearance, elegant hierarchy)
    # -------------------------------------------------------------
    
    # Helper to draw clean right-aligned commercial callout
    def draw_commercial_callout(year, bar_tip_x, line_end_x, text_anchor_x, title, desc):
        y = top_y + (year - 1957) * row_step
        svg.append(f'<line x1="{bar_tip_x:.1f}" y1="{y:.1f}" x2="{line_end_x:.1f}" y2="{y:.1f}" stroke="#666666" stroke-width="1.1"/>')
        svg.append(f'<circle cx="{bar_tip_x:.1f}" cy="{y:.1f}" r="2.5" fill="#333333"/>')
        svg.append(f'<text x="{text_anchor_x:.1f}" y="{y - 5:.1f}" font-size="15" font-weight="700" fill="#111111" text-anchor="end">{title}</text>')
        svg.append(f'<text x="{text_anchor_x:.1f}" y="{y + 12:.1f}" font-size="13" fill="#555555" text-anchor="end">{desc}</text>')

    # 1. 1980 Arianespace (bar ends at 1006.3)
    draw_commercial_callout(1980, 1006.3, 915, 905, "1980: Commercial Era Begins", "Arianespace founded as world's first commercial launch firm")

    # 2. 1995 ILS Commercial Russian Rockets (bar ends at 944.0)
    draw_commercial_callout(1995, 944.0, 850, 840, "1995: Commercial Russian Rockets", "International Launch Services (ILS) markets Proton commercially")

    # 3. 2008 SpaceX Falcon 1 (bar ends at 889.7)
    draw_commercial_callout(2008, 889.7, 800, 790, "2008: SpaceX Falcon 1 Reaches Orbit", "First privately-developed liquid-fuel rocket to reach orbit")

    # 4. 2015 Falcon 9 Booster Recovery (bar ends at 873.5, y = 1649.6)
    draw_commercial_callout(2015, 873.5, 785, 775, "2015: First Booster Recovery", "Falcon 9 first stage lands vertically, proving orbital reusability")

    # 5. 2020 Commercial Crew & Megaconstellations (Placed cleanly at y = 1718 in open white space)
    # 2020 bar is at y = 1780.6, tip at x = 799.7.
    # Text is wrapped cleanly into two lines ending before x = 400.
    # Leader line: connects from 2020 bar tip (799.7, 1780.6) -> (450, 1780.6) -> (450, 1732) -> (420, 1732)
    y_2020_bar = top_y + (2020 - 1957) * row_step # 1780.6
    y_2020_text = 1718.0
    svg.append(f'<path d="M 799.7 {y_2020_bar:.1f} L 450.0 {y_2020_bar:.1f} L 450.0 {y_2020_text + 14:.1f} L 420.0 {y_2020_text + 14:.1f}" stroke="#666666" stroke-width="1.1" fill="none"/>')
    svg.append(f'<circle cx="799.7" cy="{y_2020_bar:.1f}" r="2.5" fill="#c82274"/>')
    svg.append(f'<text x="60" y="{y_2020_text - 4:.1f}" font-size="15" font-weight="700" fill="#111111">2020: Commercial Human Spaceflight &amp; Megaconstellations</text>')
    svg.append(f'<text x="60" y="{y_2020_text + 12:.1f}" font-size="13" fill="#555555">SpaceX Crew Dragon carries NASA astronauts to the ISS;</text>')
    svg.append(f'<text x="60" y="{y_2020_text + 28:.1f}" font-size="13" fill="#555555">Starlink mass deployment accelerates in low-Earth orbit</text>')

    # 6. 2024–2026 Commercial Sector Dominance (Placed cleanly at y = 1792 in open white space)
    # Sits at x = 60 to 440, y = 1792 to 1860 (closest bar is 2021 at x = 750, 2022 at x = 655, 2023 at x = 524)
    # Leader line: drops straight down at x = 95 (well clear of all bars: 2024 tip is at 343.4, 2025 tip is at 167.5)
    # Then turns right horizontally into the tip of the peak 2025 bar (x = 167.5, y = 1911.6)
    y_2025_bar = top_y + (2025 - 1957) * row_step # 1911.6
    y_2025_text = 1792.0
    
    svg.append(f'<path d="M 95 {y_2025_text + 70:.1f} L 95 {y_2025_bar:.1f} L 165 {y_2025_bar:.1f}" stroke="#666666" stroke-width="1.2" fill="none"/>')
    svg.append(f'<circle cx="167.5" cy="{y_2025_bar:.1f}" r="2.8" fill="#c82274"/>')
    
    svg.append(f'<text x="60" y="{y_2025_text:.1f}" font-size="16" font-weight="700" fill="#111111">2024–2026: Commercial Sector Dominance</text>')
    svg.append(f'<text x="60" y="{y_2025_text + 18:.1f}" font-size="13" fill="#555555">SpaceX exceeds 130 orbital missions/year; Rocket Lab expands in US &amp; NZ;</text>')
    svg.append(f'<text x="60" y="{y_2025_text + 34:.1f}" font-size="13" fill="#555555">Chinese commercial entrants (Galactic Energy, LandSpace, CAS Space) ramp up;</text>')
    svg.append(f'<text x="60" y="{y_2025_text + 51:.1f}" font-size="13.5" font-weight="700" fill="#c82274">Commercial operators account for 77.2% of all global</text>')
    svg.append(f'<text x="60" y="{y_2025_text + 68:.1f}" font-size="13.5" font-weight="700" fill="#c82274">orbital launches in 2026 YTD</text>')

    # -------------------------------------------------------------
    # LEGEND SECTION (Spacious, larger fonts, bottom of graph)
    # -------------------------------------------------------------
    leg_y = bottom_y + 35
    leg_w = width - 120
    leg_h = 160
    
    svg.append(f'<rect x="60" y="{leg_y}" width="{leg_w}" height="{leg_h}" rx="4" fill="#fafafa" stroke="#e0e0e0" stroke-width="1.2"/>')
    
    # Row 1: Commercial Providers
    svg.append(f'<text x="80" y="{leg_y + 32}" font-size="15" font-weight="700" fill="#111111" letter-spacing="0.5">COMMERCIAL PROVIDERS (LEFT):</text>')
    private_legend_items = [
        ('SpaceX (705)', '#c82274'),
        ('Arianespace (295)', '#f26522'),
        ('ULA (174)', '#2b7bba'),
        ('Rocket Lab (82)', '#009e73'),
        ('China Commercial (81)', '#d99b00'),
        ('US Heritage Commercial (269)', '#1e4b7a'),
        ('Intl Commercial (263)', '#75588a'),
        ('US New Space (12)', '#2ca25f')
    ]
    curr_lx = 80
    for name, col in private_legend_items:
        svg.append(f'<rect x="{curr_lx}" y="{leg_y + 46}" width="18" height="14" rx="1.5" fill="{col}"/>')
        svg.append(f'<rect x="{curr_lx}" y="{leg_y + 46}" width="18" height="14" rx="1.5" fill="none" stroke="#222" stroke-width="0.5" opacity="0.3"/>')
        svg.append(f'<text x="{curr_lx + 25}" y="{leg_y + 58}" font-size="14" font-weight="500" fill="#222222">{name}</text>')
        curr_lx += len(name) * 8.6 + 36

    # Row 2: Sovereign State Operators
    svg.append(f'<text x="80" y="{leg_y + 98}" font-size="15" font-weight="700" fill="#111111" letter-spacing="0.5">SOVEREIGN STATE AGENCIES (RIGHT):</text>')
    state_legend_items = [
        ('USSR 1957–91 (2,283)', '#d12b2b'),
        ('United States (1,050)', '#1a689e'),
        ('Russia 1992+ (717)', '#8a4f9e'),
        ('China (667)', '#2e8540'),
        ('India (87)', '#e65100'),
        ('Japan (76)', '#00a2d4'),
        ('Other States (40)', '#78828c'),
        ('Europe / ESA (37)', '#59a14f')
    ]
    curr_sx = 80
    for name, col in state_legend_items:
        svg.append(f'<rect x="{curr_sx}" y="{leg_y + 112}" width="18" height="14" rx="1.5" fill="{col}"/>')
        svg.append(f'<rect x="{curr_sx}" y="{leg_y + 112}" width="18" height="14" rx="1.5" fill="none" stroke="#222" stroke-width="0.5" opacity="0.3"/>')
        svg.append(f'<text x="{curr_sx + 25}" y="{leg_y + 124}" font-size="14" font-weight="500" fill="#222222">{name}</text>')
        curr_sx += len(name) * 8.6 + 34
        
    # Launch unit note in legend
    svg.append(f'<text x="{width - 80}" y="{leg_y + 144}" font-size="13" font-weight="500" fill="#666666" text-anchor="end">1 rectangular unit tile = 1 successful orbital launch</text>')

    # -------------------------------------------------------------
    # FOOTNOTE (Neutral, academic citation)
    # -------------------------------------------------------------
    foot_y = height - 28
    svg.append(f'<text x="60" y="{foot_y}" font-size="13" fill="#666666">Source: Jonathan McDowell, General Catalog of Artificial Space Objects (GCAT, planet4589.org); data includes successful orbital launches through September 6, 2026.</text>')
    svg.append(f'<text x="{width - 60}" y="{foot_y}" font-size="13" fill="#888888" text-anchor="end">*2026 data reflects year-to-date launches through September 6, 2026.</text>')

    svg.append('</svg>')
    
    content = '\n'.join(svg)
    with open(OUTPUT_SVG, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Generated SVG: {OUTPUT_SVG}")

def render_png():
    print("Rendering SVG to PNG via Inkscape...")
    cmd = [
        'inkscape',
        OUTPUT_SVG,
        '-o', OUTPUT_PNG,
        '--export-dpi=150',
        '--export-background=#ffffff'
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode == 0:
        print(f"Successfully rendered PNG: {OUTPUT_PNG}")
    else:
        print(f"Inkscape render error:\n{res.stderr.decode('utf-8')}")

if __name__ == '__main__':
    build_svg()
    render_png()
