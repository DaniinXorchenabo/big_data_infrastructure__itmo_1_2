listener "tcp" {
  address     = "0.0.0.0:18200"
  tls_disable = "true"
}

storage "file" {
  path = "/vault/data"
}

disable_mlock = true
ui            = true
