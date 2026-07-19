$(function () {
    console.log("product_reviews.js loaded");

    function updateReviewStatistics(data) {
        $("#average-rating").text(
            Number(data.average_rating).toFixed(1)
        );

        $("#review-count").text(data.review_count);

        $("#review-label").text(
            data.review_count === 1
                ? "review"
                : "reviews"
        );
    }

    function showReviewMessage(message, isError) {
        $("#review-message")
            .removeClass(
                "alert-success alert-danger"
            )
            .addClass(
                isError
                    ? "alert alert-danger mt-3"
                    : "alert alert-success mt-3"
            )
            .text(message);
    }
    $(document).on(
        "submit",
        "#review-form",
        function (event) {
            event.preventDefault();
            event.stopPropagation();

            const $form = $(this);
            const $button = $("#review-submit-button");

            $button
                .prop("disabled", true)
                .text("Saving...");

            $.ajax({
                url: $form.attr("action"),
                type: "POST",
                data: $form.serialize(),
                dataType: "json",

                success: function (data) {
                    const $newReview = $(
                        $.parseHTML(data.review_html.trim())
                    );

                    const $existingReview = $(
                        "#review-" + data.review_id
                    );

                    if ($existingReview.length) {
                        $existingReview.replaceWith(
                            $newReview
                        );
                    } else {
                        $("#no-reviews-message").remove();
                        $("#reviews-list").prepend(
                            $newReview
                        );
                    }

                    updateReviewStatistics(data);

                    $form[0].reset();

                    $button.text("Submit Review");

                    showReviewMessage(
                        "Your review was saved successfully.",
                        false
                    );
                },

                error: function (xhr) {
                    let message =
                        "The review could not be saved.";

                    if (
                        xhr.responseJSON &&
                        xhr.responseJSON.errors
                    ) {
                        const messages = [];

                        $.each(
                            xhr.responseJSON.errors,
                            function (field, errors) {
                                $.each(
                                    errors,
                                    function (index, error) {
                                        messages.push(
                                            error.message
                                        );
                                    }
                                );
                            }
                        );

                        message = messages.join(" ");
                    }

                    showReviewMessage(
                        message,
                        true
                    );
                },

                complete: function () {
                    $button
                        .prop("disabled", false);

                    if (
                        $button.text() === "Saving..."
                    ) {
                        $button.text("Submit Review");
                    }
                }
            });

            return false;
        }
    );

    $(document).on(
        "click",
        ".review-edit-button",
        function () {
            const $review = $(this).closest(
                "article"
            );

            $("#review-rating").val(
                $review.attr("data-rating")
            );

            $("#review-comment").val(
                $review
                    .find(".review-comment-data")
                    .text()
                    .trim()
            );

            $("#review-submit-button").text(
                "Update Review"
            );

            $("html, body").animate(
                {
                    scrollTop:
                        $("#review-form").offset().top -
                        100
                },
                400
            );
        }
    );

    $(document).on(
        "submit",
        ".delete-review-form",
        function (event) {
            event.preventDefault();
            event.stopPropagation();

            const $form = $(this);
            const $review = $form.closest(
                "article"
            );

            if (!window.confirm("Delete your review?")) {
                return false;
            }

            const $button = $form.find(
                "button[type='submit']"
            );

            $button
                .prop("disabled", true)
                .text("Deleting...");

            $.ajax({
                url: $form.attr("action"),
                type: "POST",
                data: $form.serialize(),
                dataType: "json",

                success: function (data) {
                    $review.remove();

                    updateReviewStatistics(data);

                    if (data.review_count === 0) {
                        $("#reviews-list").append(
                            '<p id="no-reviews-message" ' +
                            'class="text-secondary">' +
                            "This product does not have " +
                            "any reviews yet." +
                            "</p>"
                        );
                    }

                    $("#review-form")[0].reset();

                    $("#review-submit-button").text(
                        "Submit Review"
                    );

                    showReviewMessage(
                        "Your review was deleted.",
                        false
                    );
                },

                error: function () {
                    $button
                        .prop("disabled", false)
                        .text("Delete");

                    showReviewMessage(
                        "The review could not be deleted.",
                        true
                    );
                }
            });

            return false;
        }
    );
});