output "ips" {
  value = [aws_instance.mail-server.*.public_ip]
}
