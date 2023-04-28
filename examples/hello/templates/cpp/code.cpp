#include "{{ name }}.h"

#include <iostream>

using namespace std;

void {{ name }}()
{
    {% for line in content %}
    cout << "{{ line }}" << endl;
    {% endfor %}
}