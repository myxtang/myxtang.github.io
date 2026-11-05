---
layout: clean-page
permalink: /publications/
title: publications
nav: true
nav_order: 2
compact_pubs: true # compact list: no thumbnails, no journal/conference tags (see _layouts/clean-bib.liquid)
---

<!--
  Three lists, each in the order of _bibliography/papers.bib (keep newest first) and numbered from the bottom
  like a CV: @article = Journal papers [J#], @inproceedings = Conference papers [C#],
  @unpublished or @misc = Submitted and preprints [S#]. A section only appears once it has an entry.
-->

{% capture n_journal %}{% bibliography_count --query @article %}{% endcapture %}
{% capture n_conf %}{% bibliography_count --query @inproceedings @incollection @conference %}{% endcapture %}
{% capture n_pre %}{% bibliography_count --query @unpublished @misc %}{% endcapture %}
{% assign n_journal = n_journal | strip | plus: 0 %}
{% assign n_conf = n_conf | strip | plus: 0 %}
{% assign n_pre = n_pre | strip | plus: 0 %}

<div class="publications compact">

{% if n_journal > 0 %}
<section class="pub-sec journal" style="counter-reset: pub {{ n_journal | plus: 1 }}">
<h2>Journal papers</h2>
{% bibliography --group_by none --query @article %}
</section>
{% endif %}

{% if n_conf > 0 %}
<section class="pub-sec conference" style="counter-reset: pub {{ n_conf | plus: 1 }}">
<h2>Conference papers</h2>
{% bibliography --group_by none --query @inproceedings @incollection @conference %}
</section>
{% endif %}

{% if n_pre > 0 %}
<section class="pub-sec preprint" style="counter-reset: pub {{ n_pre | plus: 1 }}">
<h2>Submitted &amp; preprints</h2>
{% bibliography --group_by none --query @unpublished @misc %}
</section>
{% endif %}

</div>
