{{/*
Full name of a release-scoped resource.
*/}}
{{- define "zato.fullname" -}}
{{- if contains .Chart.Name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Common labels.
*/}}
{{- define "zato.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{ include "zato.selectorLabels" . }}
{{- end }}

{{/*
Selector labels.
*/}}
{{- define "zato.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Name of the Secret holding the environment's password.
*/}}
{{- define "zato.passwordSecretName" -}}
{{- if .Values.password.existingSecret }}
{{- .Values.password.existingSecret }}
{{- else }}
{{- include "zato.fullname" . }}
{{- end }}
{{- end }}
