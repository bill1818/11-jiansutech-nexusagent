from jinja2 import Template


def create_url_template(dic):
    url = '/service/rest/v1/search/assets?group={{ component_group }}&name={{ component_name }}&version={{ component_version }}&maven.extension=jar'

    template = Template(url)
    template_content = template.render(**dic)

    return template_content
