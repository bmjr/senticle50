from classifiers.models import ClassifiedDay


class ClassifiedDayTransformer:
    """ A Transformer layer class used to transform attributes into a
        ClassifiedDay model.
    """

    @staticmethod
    def get_classified_day(date, classification_type_id, classification_value,
                           amount_classified):
        """
        Transforms given arguments into a classified day object or none where
        an identical ClassifiedDay object already exists.

        Args:
            :param date: The date of the classified Day
            :param classification_type_id: The classification type id
                   of the classified day
            :param classification_value: The classification value
                   of the classified day
            :param amount_classified: The amount classified for the
                   given classification value of the classified day

        Returns:
            None: Where an existing ClassifiedDay row already exists
                  that is identical in every attribute
            ClassifiedDay (Model Object): Where an entry does not
                  currently exist for the given ClassifiedDay attributes.
        """

        try:
            classified_day = ClassifiedDay.objects.get(
                date=date,
                classification_type_id=classification_type_id,
                classification_value=classification_value)

            # Check if Update Required
            if classified_day.amount_classified == amount_classified:
                # Identical ClassifiedDay already exists
                return None
            else:
                # ClassifiedDay already exists but attributes are different so
                # return the new ClassifiedDay.
                classified_day.amount_classified = amount_classified
                return classified_day

        except ClassifiedDay.DoesNotExist:
            # Create Classified Day where one doesn't exist.
            return ClassifiedDay(
                date=date,
                classification_value=classification_value,
                classification_type_id=classification_type_id,
                amount_classified=amount_classified
            )
