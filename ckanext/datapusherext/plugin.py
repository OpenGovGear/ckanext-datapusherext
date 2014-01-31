import logging

import ckan.plugins as p
import ckanext.datapusherext.logic.action as action
import ckan.logic.action.update as core_update
import ckanext.datapusherext.logic.auth as auth
import ckanext.datapusherext.helpers as helpers
import ckan.logic as logic
import ckan.model as model
import ckan.common as common

log = logging.getLogger(__name__)
_get_or_bust = logic.get_or_bust

DEFAULT_FORMATS = ['csv', 'xls', 'application/csv', 'application/vnd.ms-excel']


class DatastoreException(Exception):
    pass

class DatapusherPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IActions)
    p.implements(p.IAuthFunctions)
    p.implements(p.IResourceUrlChange)
    p.implements(p.IDomainObjectModification, inherit=True)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IRoutes, inherit=True)

    legacy_mode = False
    resource_show_action = None

    def configure(self, config):
        self.config = config

        datapusher_formats = config.get('ckan.datapusher.formats', '').lower()
        self.datapusher_formats = datapusher_formats.split() or DEFAULT_FORMATS

        datapusher_url = config.get('ckan.datapusher.url')
        if not datapusher_url:
            raise Exception(
                'Config option `ckan.datapusher.url` has to be set.')

        if not datapusher_url:
            raise Exception(
                'Config option `ckan.datapusher.secret_key` has to be set.')

    def resource_update(self, context, data_dict):
        resource = core_update.resource_update(context, data_dict)
        try:
            context = {'model': model, 'ignore_auth': True}
            if resource.get('format','').lower() in self.datapusher_formats:
                p.toolkit.get_action('datapusher_submit')(context, {
                    'resource_id': resource['id']
                })
        except p.toolkit.ValidationError, e:
            # If datapusher is offline want to catch error instead
            # of raising otherwise resource save will fail with 500
            log.critical(e)
            pass

        return resource

    def notify(self, entity, operation=None):
        if isinstance(entity, model.Resource):
            if (operation == model.domain_object.DomainObjectOperation.new
                    or not operation):
                # if operation is None, resource URL has been changed, as
                # the notify function in IResourceUrlChange only takes
                # 1 parameter
                context = {'model': model, 'ignore_auth': True,
                           'defer_commit': True}
                try:
                    context.setdefault('user', common.c.user or common.c.author)
                except TypeError:
                    site_user = p.toolkit.get_action('get_site_user')(context, {})
                    context.setdefault('user', site_user['name'])

                if (entity.format and
                    entity.format.lower() in self.datapusher_formats):
                    try:
                        p.toolkit.get_action('datapusher_submit')(context, {
                            'resource_id': entity.id
                        })
                    except p.toolkit.ValidationError, e:
                        # If datapusher is offline want to catch error instead
                        # of raising otherwise resource save will fail with 500
                        log.critical(e)
                        pass

    def before_map(self, m):
        m.connect(
            'resource_data', '/dataset/{id}/resource_data/{resource_id}',
            controller='ckanext.datapusher.plugin:ResourceDataController',
            action='resource_data')
        return m

    def get_actions(self):
        return {'datapusher_submit': action.datapusher_submit,
                'datapusher_hook': action.datapusher_hook,
                'datapusher_status': action.datapusher_status,
                'resource_update': self.resource_update}

    def get_auth_functions(self):
        return {'datapusher_submit': auth.datapusher_submit,
                'datapusher_status': auth.datapusher_status}

    def get_helpers(self):
        return {
            'datapusher_status': helpers.datapusher_status}
