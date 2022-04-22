# prometheus alertreceiver webhook2mail

[Openshift alert receivers](https://docs.openshift.com/container-platform/4.9/monitoring/managing-alerts.html#configuring-alert-receivers_managing-alerts) can only be managed by cluster admins in the secret `alertmanager-main` in the namespace `openshift-monitoring`.  
__paw2mail__ is a webservice that accepts alerts and sends them to an email address.


## config

The receiver email adress is defined in `label paw2mail`:

```
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: foo
spec:
  groups:
    - name: bar
      rules:
        - alert: foobar_is_bigger_42
          expr: 'example_count_total{item_type="/count"} > 42'
          labels:
            severity: Info
            paw2mail: jon@example.net
```

## Setup

Needed environments

```
export smtp_from=cluster@example.net
export smtp_host=mail.example.net
export smtp_port=25
```

Optional
```
export smtp_user=clustermailer
export smtp_pass=xxxxxxxxxxxxx
```