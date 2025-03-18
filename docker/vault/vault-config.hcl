listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = "true"
  scheme = "http"
}

storage "file" {
  path = "/vault/data"
}
path "dev/data/daniil" {
  capabilities = ["read", "list"]
}

disable_mlock = true
ui            = true
