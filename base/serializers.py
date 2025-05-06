from rest_framework.relations import SlugRelatedField
from rest_framework import serializers
from django.db import IntegrityError


class IExactCreatableSlugRelatedField(SlugRelatedField):
    """
    A SlugRelatedField that performs case-insensitive lookups and can create 
    new objects if they don't exist.
    
    This field supports using a case-insensitive lookup (iexact) to find an existing
    object, and if not found, creates a new object with the provided value.
    """
    
    def to_internal_value(self, data):
        if not data:
            return None
            
        try:
            data = str(data).strip()
            queryset = self.get_queryset()
            
            # First try to find with case-insensitive lookup
            try:
                filter_kwargs = {f"{self.slug_field}__iexact": data}
                return queryset.get(**filter_kwargs)
            except queryset.model.DoesNotExist:
                # Create new object if not found
                try:
                    create_kwargs = {self.slug_field: data}
                    return queryset.create(**create_kwargs)
                except IntegrityError as e:
                    # Handle potential race condition or other integrity errors
                    raise serializers.ValidationError(
                        f"Failed to create {queryset.model.__name__} with {self.slug_field}='{data}': {str(e)}"
                    )
        except (TypeError, ValueError) as e:
            self.fail("invalid")
        except Exception as e:
            raise serializers.ValidationError(f"Error processing value '{data}': {str(e)}")


class ReadWriteSerializerMethodField(serializers.SerializerMethodField):
    """
    A SerializerMethodField that can also accept writes by calling a method on the serializer.
    
    For read operations, it works like a regular SerializerMethodField.
    For write operations, it calls `<field_name>_setter` method on the serializer.
    """
    
    def __init__(self, method_name=None, setter_method_name=None, **kwargs):
        self.setter_method_name = setter_method_name
        super().__init__(method_name, **kwargs)
        
    def to_internal_value(self, data):
        if not self.setter_method_name and not hasattr(self.parent, f'{self.method_name}_setter'):
            raise serializers.ValidationError(f"Method '{self.method_name}_setter' not found on {self.parent.__class__.__name__}")
            
        setter = getattr(self.parent, self.setter_method_name or f'{self.method_name}_setter')
        return setter(data)
