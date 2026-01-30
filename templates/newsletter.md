# {{ newsletter_name }}
**Week {{ week_number }} | {{ date }}**

---

## This Week at a Glance

- **{{ item_count }}** items collected from {{ source_count }} sources
- **Top themes**: {{ themes }}

---

## 🔥 Top Stories

{% for item in top_stories %}
### {{ loop.index }}. [{{ item.title }}]({{ item.url }})

**{{ item.source_name }}** | {{ item.date }}
{% if item.score > 0 %}⬆️ {{ item.score }} | 💬 {{ item.num_comments }}{% endif %}

{% if item.summary %}
> {{ item.summary }}
{% endif %}

{% endfor %}

---

## 📚 Research Highlights

{% for item in research %}
### [{{ item.title }}]({{ item.url }})

*{{ item.author }}*

> {{ item.summary }}

{% if item.pdf_url %}📄 [PDF]({{ item.pdf_url }}){% endif %}

{% endfor %}

---

## 💬 Community Buzz

{% for item in discussions %}
**[{{ item.title }}]({{ item.url }})**

{{ item.source_name }} | ⬆️ {{ item.score }} | 💬 {{ item.num_comments }}

{% endfor %}

---

## 🔗 Quick Links

{% for item in quick_links %}
- [{{ item.title }}]({{ item.url }}) *({{ item.source_name }})*
{% endfor %}

---

*Generated on {{ generated_at }}*

*This newsletter was compiled using the Weekly Newsletter Builder.*
