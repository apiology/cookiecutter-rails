require "cache_method"
require "redis"

cachemethod_storage = Redis.new(host: ENV.fetch("REDIS_HOSTNAME", nil),
                                port: ENV.fetch("REDIS_PORT", nil),
                                username: ENV.fetch("REDIS_USERNAME", nil),
                                password: ENV.fetch("REDIS_PASSWORD", nil))
CacheMethod.config.storage = cachemethod_storage

require "checkoff/monkeypatches/resource_marshalling"
