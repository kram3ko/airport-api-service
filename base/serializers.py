from rest_framework.relations import SlugRelatedField


class IExactCreatableSlugRelatedField(SlugRelatedField):
    def to_internal_value(self, data):
        queryset = self.get_queryset()
        try:
            data = str(data).strip()

            if not data:
                return None

            filter_dict = {
                f"{self.slug_field}__iexact": data,
                "defaults": {self.slug_field: data},
            }
            obj, _ = queryset.get_or_create(**filter_dict)

            return obj
        except (TypeError, ValueError):
            self.fail("invalid")
