# Slide Type Components

Markup for every slide component in the ALPA design system. Use these structures verbatim when composing slides — only the text/data content changes.

**Eyebrow** — small bold label directly above the heading:
```html
<div class="eyebrow">Eyebrow Text</div>
<h2>The heading below</h2>
```
Always placed inside `.content`, immediately before the `<h2>`.

**Heading + Body** — the most common slide: heading with paragraph below:
```html
<div class="content">
    <div class="eyebrow">Eyebrow Text</div>
    <h2>The heading states the insight</h2>
    <p>Supporting paragraph with context and detail. Keep it to 2-3 lines max.</p>
</div>
```

**Heading + List** — bullet list below a heading:
```html
<div class="content">
    <h2>What we need to answer</h2>
    <ul class="body-list">
        <li>First question or point</li>
        <li>Second question or point</li>
        <li>Third question or point</li>
    </ul>
</div>
```

**Heading + Stats** — vertical stat list (not cards):
```html
<div class="content">
    <h2>Who do we build for?</h2>
    <p>Context paragraph explaining what the numbers mean.</p>
    <div class="stat-list">
        <div class="stat-line">8,211 employees</div>
        <div class="stat-line">3,313 contingent workers</div>
        <div class="stat-line bold">11,524 total workforce</div>
    </div>
</div>
```

**Stat Row** — large numbers in columns with labels (centered layout):
```html
<div class="stat-row">
    <div class="stat-col">
        <div class="stat-title">Bay Area</div>
        <div class="stat-value">50%</div>
        <div class="stat-label">Share of workforce</div>
    </div>
    <div class="stat-col">
        <div class="stat-title">Americas</div>
        <div class="stat-value">13%</div>
        <div class="stat-label">Share of workforce</div>
    </div>
</div>
```

**Stat Comparison** — before/after with arrows and change indicators:
```html
<div class="stat-row">
    <div class="stat-col">
        <div class="stat-title">Bay Area</div>
        <div class="stat-value muted">50%</div>
        <div class="stat-label">Share of workforce</div>
        <div class="stat-arrow">&#8595;</div>
        <div class="stat-value">32%</div>
        <div class="stat-change negative">-26% &#9660;</div>
    </div>
    <div class="stat-col">
        <div class="stat-title">Americas</div>
        <div class="stat-value muted">13%</div>
        <div class="stat-label">Share of workforce</div>
        <div class="stat-arrow">&#8595;</div>
        <div class="stat-value">26%</div>
        <div class="stat-change positive">+115% &#9650;</div>
    </div>
</div>
```

**Heading + Stat Row** — eyebrow + heading with columnar stats below. Same vertical rhythm as timeline slides. Use `.slide.centered`:
```html
<div class="slide centered">
    <div class="content">
        <div class="eyebrow">Section</div>
        <h2>Perfil del comprador</h2>
        <div class="stat-row">
            <div class="stat-col">
                <div class="stat-title">Label</div>
                <div class="stat-value">50%</div>
                <div class="stat-label">Description text</div>
            </div>
            <div class="stat-col">
                <div class="stat-title">Label</div>
                <div class="stat-value">30%</div>
                <div class="stat-label">Description text</div>
            </div>
        </div>
    </div>
    <div class="brand-mark">ALPA</div>
</div>
```
The `.slide.centered .content h2` rule tightens the heading's bottom margin so the heading sits close to the stat-row, matching the timeline layout.

**Statement** — bold centered text on white or dark:
```html
<!-- White statement -->
<div class="slide">
    <div class="statement">We talk about flexibility but design for predictability.</div>
</div>

<!-- Dark statement -->
<div class="slide dark">
    <div class="statement">People don't connect to policies. They connect to places, to their work, and to each other.</div>
</div>
```

**Data Table** — clean table with dotted borders:
```html
<div class="content">
    <h2>Bay Area: Workforce & Footprint Shifts ('20 - '25)</h2>
    <table class="data-table">
        <thead><tr><th>Cities</th><th>Workforce Today</th><th>Change</th><th>Ratio</th></tr></thead>
        <tbody>
            <tr><td>San Francisco</td><td>2,330</td><td class="negative">-26% &#9660;</td><td>1 : 108</td></tr>
            <tr class="total-row"><td></td><td><strong>2,330</strong></td><td class="negative">-26% &#9660;</td><td><strong>1 : 108</strong></td></tr>
        </tbody>
    </table>
</div>
```

**Insight List** — numbered items with bold lead:
```html
<div class="content">
    <h2>Key findings</h2>
    <ul class="insight-list">
        <li><span class="num">01</span><span><span class="emphasis">Bold lead</span> — supporting detail after the dash</span></li>
    </ul>
</div>
```

**Bar Chart** — horizontal bars with labels and values:
```html
<div class="content">
    <h2>Distribution</h2>
    <div class="bar-chart">
        <div class="bar-row">
            <span class="bar-label">Label</span>
            <div class="bar-track"><div class="bar-fill accent" style="width:73%"></div></div>
            <span class="bar-value">73%</span>
        </div>
    </div>
</div>
```

**Timeline** — phased progression:
```html
<div class="timeline">
    <div class="timeline-item active">
        <div class="timeline-dot"></div>
        <div class="timeline-label">Phase 1</div>
        <div class="timeline-title">Title</div>
        <div class="timeline-desc">Description</div>
    </div>
</div>
```

**Two Column** — side by side content areas:
```html
<div class="two-col">
    <div><!-- left content --></div>
    <div><!-- right content --></div>
</div>
```

**Comparison** — side by side with arrow:
```html
<div class="comparison">
    <div class="comparison-side">
        <div class="comparison-label">Before</div>
        <div class="comparison-content">Description</div>
    </div>
    <div class="comparison-arrow">&#8594;</div>
    <div class="comparison-side highlight">
        <div class="comparison-label">After</div>
        <div class="comparison-content">Description</div>
    </div>
</div>
```

**Callout** — inline annotation:
```html
<div class="callout">Key takeaway or footnote.</div>
```

**Image — Full Bleed** — single image filling the entire slide:
```html
<div class="slide image-slide">
    <img src="image-url.jpg" alt="Description" />
</div>
```

**Image — Full Bleed + Title** — full-bleed image with overlaid title (like a cover or statement). Use `.image-title-slide`:
```html
<div class="slide image-title-slide">
    <img src="image-url.jpg" alt="Description" />
    <div class="image-title-overlay">
        <h1>Title Goes Here</h1>
        <p class="subtitle">Optional subtitle</p>
    </div>
    <div class="brand-mark">ALPA</div>
</div>
```

**Image — Split 2** — two images side by side with white border:
```html
<div class="slide image-grid cols-2">
    <img src="image1.jpg" alt="" />
    <img src="image2.jpg" alt="" />
</div>
```

**Image — Split 3** — three images in a row:
```html
<div class="slide image-grid cols-3">
    <img src="image1.jpg" alt="" />
    <img src="image2.jpg" alt="" />
    <img src="image3.jpg" alt="" />
</div>
```

**Image — Split 4** — two rows of two:
```html
<div class="slide image-grid cols-2 rows-2">
    <img src="image1.jpg" alt="" />
    <img src="image2.jpg" alt="" />
    <img src="image3.jpg" alt="" />
    <img src="image4.jpg" alt="" />
</div>
```

**Image — Split 6** — two rows of three:
```html
<div class="slide image-grid cols-3 rows-2">
    <img src="image1.jpg" alt="" />
    <img src="image2.jpg" alt="" />
    <img src="image3.jpg" alt="" />
    <img src="image4.jpg" alt="" />
    <img src="image5.jpg" alt="" />
    <img src="image6.jpg" alt="" />
</div>
```
