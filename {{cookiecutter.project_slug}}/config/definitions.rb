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
#       # @param versions [Symbol, Hash<Symbol, [Number, Boolean]>]
#       # @param block [Proc]
#       # @param layout [Boolean]
#       # @param status [Symbol]
#       # @param options [Hash]
#       # @return [void]
#       def allow_browser(versions:,
#                         block: -> { render file: Rails.root.join("public/406-unsupported-browser.html"), layout: false, status: :not_acceptable },
#                         **options)
#       end
#   end
#   class ActiveRecord::Relation
#     # @return [ActiveRecord::Base]
#     def find_or_create_by(**attributes, &block); end
#     include Enumerable
#     # @return [ActiveRecord::Result]
#     def records; end
#     # @see ActiveRecord::Result#each
#     # @return [void]
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
#       # @return [void]
#       def configure(&block); end
#     end
#     class Application < Engine
#       # @yieldself [Rails::Application]
#       # @return [void]
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
#         def before_action(*names, &block); end
#         # @param names [Array<Symbol>]
#         # @return [void]
#         def prepend_before_action(*names, &block); end
#         # @param names [Array<Symbol>]
#         # @return [void]
#         def skip_before_action(*names, &block); end
#         # @param names [Array<Symbol>]
#         # @return [void]
#         def around_action(*names, &block); end
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
