from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response


class CreateDeleteRecordMixin:

    def create_delete_record(
        self,
        request,
        pair_model,
        user_model,
        through_model,
        pair_field,
        serializer,
        exist_message,
        pk=None
    ):
        pair = get_object_or_404(pair_model, pk=pk)
        if request.method == 'POST':
            if through_model.objects.filter(
                user=request.user, **{pair_field: pair}
            ).exists():
                return Response(
                    exist_message, status=status.HTTP_400_BAD_REQUEST
                )
            obj = through_model.objects.get_or_create(
                user=request.user, **{pair_field: pair}
            )
            serializer = serializer(instance=pair)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        obj = get_object_or_404(
            through_model, user=request.user,
            **{pair_field: pair}
        )
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
