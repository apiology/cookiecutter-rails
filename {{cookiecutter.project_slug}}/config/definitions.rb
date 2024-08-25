# https://gist.github.com/castwide/28b349566a223dfb439a337aea29713e
#
# The following comments fill some of the gaps in Solargraph's understanding of
# Rails apps. Since they're all in YARD, they get mapped in Solargraph but
# ignored at runtime.
#
# You can put this file anywhere in the project, as long as it gets included in
# the workspace maps. It's recommended that you keep it in a standalone file
# instead of pasting it into an existing one.
#
# we copy from upstream places, so ignore long lines
#
# rubocop:disable Layout/LineLength
# @!parse
#   class ActionController::API
#     include ActionController::MimeResponds
#     include ActionController::Base
#     include ActionController::Renderer
#     extend ActiveSupport::Callbacks::ClassMethods
#     extend AbstractController::Callbacks::ClassMethods
#   end
#   class ActionController::Base
#     include ActionController::MimeResponds
#     include ActionController::Metal
#     include ActionController::Rendering
#     include ActionController::Head
#     extend ActionController::AllowBrowser::ClassMethods
#     extend ActiveSupport::Callbacks::ClassMethods
#     extend AbstractController::Callbacks::ClassMethods
#   end
#   class ActiveRecord::Base
#     extend ActiveModel::Validations::ClassMethods
#     extend ActiveRecord::Encryption::EncryptableRecord
#     extend ActiveRecord::QueryMethods
#     extend ActiveRecord::FinderMethods
#     extend ActiveRecord::Associations::ClassMethods
#     extend ActiveRecord::Inheritance::ClassMethods
#     extend ActiveRecord::Scoping::Named::ClassMethods
#     extend ActiveRecord::Callbacks::ClassMethods
#     extend ActiveRecord::Relation
#     include ActiveRecord::AttributeMethods::PrimaryKey
#     include ActiveRecord::Persistence
#   end
#   class ActiveJob::Base
#     extend ActiveJob::Core::ClassMethods
#     extend ActiveJob::QueueName::ClassMethods
#     extend ActiveJob::Enqueuing::ClassMethods
#   end
#   class ActionController::AllowBrowser::ClassMethods
#       # @return [void]
#       def allow_browser(versions:,
#                         block: -> { render file: Rails.root.join("public/406-unsupported-browser.html"), layout: false, status: :not_acceptable },
#                         **options)
#       end
#   end
#   class ActiveRecord::Relation
#     def find_or_create_by(**attributes, &block); end
#     include Enumerable
#     # @return [ActiveRecord::Result]
#     def records; end
#     # @see ActiveRecord::Result#each
#     def each(&block); end
#   end
#   class ActiveRecord::Result
#     include Enumerable
#   end
#
#   require 'logger'
#
#   module ::Rails
#     class << self
#       # @return [Logger]
#       def logger; end
#     end
#     class << self
#       # @return [Rails::Application]
#       def application; end
#     end
#     class Railtie
#       # @yieldself [Rails::Application]
#       def configure(&block); end
#     end
#   end
#
# @!override ActiveRecord::FinderMethods#find
#   @overload find(id)
#     @param id [Integer]
#     @return [self]
#   @overload find(list)
#     @param list [Array]
#     @return [Array<self>]
#   @overload find(*args)
#     @return [Array<self>]
#   @return [self, Array<self>]
#
# @!override ActiveRecord::Scoping::Named::ClassMethods#all
#   @return [ActiveRecord::Relation]
#
# @!override ActiveRecord::QueryMethods#where
#   @return [ActiveRecord::Relation]
#
# @!parse
#   module AbstractController
#     module Callbacks
#       module ClassMethods
#         # @param names [Array<Symbol>]
#         # @return [void]
#         def prepend_before_action(*names, &block); end
#         # @param names [Array<Symbol>]
#         # @return [void]
#         def skip_before_action(*names, &block); end
#       end
#     end
#   end
#
# @!override ActionController::Base#request
#   @return [ActionDispatch::Request]
#
# @!override ActionDispatch::Request#headers
#   @return [Http::Headers]
#
# @!override ActionDispatch::Http::Headers#fetch
#   @param key [String]
#   @return [String]
#
# @!override ActionController::Metal#params
#   @return [Hash<[String,Symbol],String>]
#
# @!override Hash<[String,Symbol],String>#fetch
#   @return [String>]
#
# @!parse
#   module Asana
#     class Client
#       # @return [Asana::ProxiedResourceClasses::Task]
#       def tasks; end
#       # @return [Asana::ProxiedResourceClasses::Webhook]
#       def webhooks; end
#     end
#     module Resources
#       class Task
#         # @return [String, nil]
#         def html_notes; end
#       end
#     end
#     module ProxiedResourceClasses
#       class Task
#         # Returns the complete task record for a single task.
#         #
#         # @param id [String] The task to get.
#         # @param options [Hash] the request I/O options.
#         # @return [Asana::Resources::Task]
#         def find_by_id(id, options: {}); end
#       end
#     end
#     module ProxiedResourceClasses
#       class Webhook
#         # Returns the compact representation of all webhooks your app has
#         # registered for the authenticated user in the given workspace.
#         #
#         # @param workspace [String] The workspace to query for webhooks in.
#         # @param resource [String] Only return webhooks for the given resource.
#         # @param per_page [Integer] the number of records to fetch per page.
#         # @param options [Hash] the request I/O options.
#         # @return [Array<Asana::Resources::Webhook>]
#         def get_all(workspace: required("workspace"), resource: nil, per_page: 20, options: {})
#         end
#         # @param options [Hash] the request I/O options
#         # @param opt_fields [List<str>]  Defines fields to return.
#         # @param opt_pretty [Boolean]  Provides “pretty” output.
#         # @param data [Hash] the attributes to POST
#         # @return [Asana::Resources::Webhook]
#         def create_webhook(client, options: {}, **data)
#         end
#       end
#     end
#   end
#   class ENV
#     # @param key [String]
#     # @param default [Object]
#     #
#     # @return [Object,nil]
#     def self.fetch(key, default = :none); end
#     # @param key [String]
#     #
#     # @return [Object,nil]
#     def self.[](key); end
#   end
# rubocop:enable Layout/LineLength
