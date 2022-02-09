JUNOS_URL='{0}:{1}/rpc{2}'
SCHEMAS={
   "config":"<lock-configuration/><load-configuration>{0}</load-configuration><commit/><unlock-configuration/>",
   "append-address-book":"<configuration><security><address-book><name>{0}</name><address><name>{1}</name><ip-prefix>{2}</ip-prefix></address></address-book></security></configuration>"
}