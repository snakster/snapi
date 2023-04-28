def {{ name }}():
    {% for line in content %}
    print("{{ line }}")
    {% endfor %}