from django.db import models

class ZornaFolderManager(models.Manager):

    def on_site(self, site_id=None):
        return self.all()

    def root(self):
        """Return a :class:`QuerySet` of folder without parent."""
        return self.on_site().filter(parent__isnull=True)

    def from_path(self, complete_path):
        """
        return folder from complete path
        otherwise returns None 
        """
        if complete_path == None or complete_path == '':
            return None
        if complete_path.endswith("/"):
            complete_path = complete_path[:-1]

        if complete_path == '':
            root_categories = self.root()
            if root_categories:
                return root_categories[0]
            else:
                return None
        slug = complete_path.split("/")[-1]
        folders_list = self.on_site().filter(slug=slug)

        category_ret = None
        if len(folders_list) == 1 :
            category_ret = folders_list[0]
        elif len(folders_list) > 1 :
            for category in folders_list:
                pp = category.get_complete_slug() + slug
                if category and pp == complete_path:
                    category_ret = category
                    break
        return category_ret
