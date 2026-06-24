for outfit in payload["outfits"]:
    st.subheader(
        f"Compatibility Score: {outfit['compatibility_score']}/100"
    )

    if outfit.get("generated_image_path"):
        st.caption("Generated Outfit Board")
        st.code(outfit["generated_image_path"])

        safe_image(
            outfit["generated_image_path"],
            "Generated outfit board from dataset images",
        )

    for reason in outfit["reasoning"]:
        st.write(reason)

    cols = st.columns(4)

    for index, slot in enumerate(["topwear", "bottomwear", "footwear"]):
        item = outfit.get(slot)

        with cols[index]:
            st.caption(slot.upper())

            if item:
                if item.get("image_path"):
                    safe_image(item["image_path"])

                st.metric(
                    item["name"],
                    f"{item['score']}/100"
                )

                shown_ids.append(item["id"])

                st.write(
                    f"{item['color']} "
                    f"{item['article_type']} | "
                    f"{item['usage']} | "
                    f"{item['season']}"
                )

                st.progress(
                    min(item["score"] / 100, 1.0)
                )

    with cols[3]:
        st.caption("ACCESSORY")

        for item in outfit.get("accessories", []):
            if item.get("image_path"):
                safe_image(item["image_path"])

            st.metric(
                item["name"],
                f"{item['score']}/100"
            )

            shown_ids.append(item["id"])

    with st.expander("Score breakdown"):
        st.json(outfit)
