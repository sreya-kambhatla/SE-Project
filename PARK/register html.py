{% extends "base.html" %}
{% block content %}
<form method="POST" action="">
    {{ form.hidden_tag() }}
    {{ form.username.label }} {{ form.username() }}
    {{ form.email.label }} {{ form.email() }}
    {{ form.password.label }} {{ form.password() }}
    {{ form.confirm_password.label }} {{ form.confirm_password() }}
    {{ form.submit() }}
</form>
{% endblock %}
