package com.tskhra.modulith.trade_module.elastic.documents;

import com.tskhra.modulith.trade_module.model.domain.TradeCategory;
import com.tskhra.modulith.trade_module.model.domain.Item;
import com.tskhra.modulith.trade_module.model.domain.ItemImage;
import com.tskhra.modulith.trade_module.model.enums.ItemCondition;
import com.tskhra.modulith.trade_module.model.enums.ItemStatus;
import com.tskhra.modulith.trade_module.model.enums.TradeRange;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.elasticsearch.annotations.DateFormat;
import org.springframework.data.elasticsearch.annotations.Document;
import org.springframework.data.elasticsearch.annotations.Field;
import org.springframework.data.elasticsearch.annotations.FieldType;
import org.springframework.data.elasticsearch.annotations.Setting;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Document(indexName = "items_index")
@Setting(settingPath = "elasticsearch/item-settings.json")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ItemDocument {

    @Id
    private UUID id;

    @Field(type = FieldType.Long)
    private Long ownerId;

    @Field(type = FieldType.Text, analyzer = "item_analyzer", searchAnalyzer = "item_search_analyzer")
    private String name;

    @Field(type = FieldType.Text, analyzer = "item_analyzer", searchAnalyzer = "item_search_analyzer")
    private String description;

    @Field(type = FieldType.Integer)
    private Integer categoryId;

    @Field(type = FieldType.Keyword)
    private String categoryName;

    @Field(type = FieldType.Long)
    private Long cityId;

    @Field(type = FieldType.Keyword)
    private String cityName;

    @Field(type = FieldType.Keyword)
    private List<String> imageUris;

    @Field(type = FieldType.Integer)
    private List<Integer> desiredCategoryIds;

    @Field(type = FieldType.Integer)
    private Integer itemTypeId;

    @Field(type = FieldType.Keyword)
    private String itemTypeName;

    @Field(type = FieldType.Object, enabled = false)
    private Map<String, Object> specifications;

    @Field(type = FieldType.Double)
    private BigDecimal estimatedValue;

    @Field(type = FieldType.Double)
    private BigDecimal valueVarianceRatio;

    @Field(type = FieldType.Keyword)
    private ItemCondition condition;

    @Field(type = FieldType.Keyword)
    private TradeRange tradeRange;

    @Field(type = FieldType.Keyword)
    private ItemStatus status;

    @Field(type = FieldType.Date, format = DateFormat.date_hour_minute_second_millis)
    private LocalDateTime createdAt;

    @Field(type = FieldType.Date, format = DateFormat.date_hour_minute_second_millis)
    private LocalDateTime updatedAt;

    public static ItemDocument fromEntity(Item item) {
        return ItemDocument.builder()
                .id(item.getId())
                .ownerId(item.getOwnerId())
                .name(item.getName())
                .description(item.getDescription())
                .categoryId(item.getCategory() != null ? item.getCategory().getId() : null)
                .categoryName(item.getCategory() != null ? item.getCategory().getName() : null)
                .cityId(item.getCity() != null ? item.getCity().getId() : null)
                .cityName(item.getCity() != null ? item.getCity().getName() : null)
                .imageUris(item.getImages() != null
                        ? item.getImages().stream().map(ItemImage::getUri).toList()
                        : List.of())
                .desiredCategoryIds(item.getDesiredCategories() != null
                        ? item.getDesiredCategories().stream().map(TradeCategory::getId).toList()
                        : List.of())
                .itemTypeId(item.getItemType() != null ? item.getItemType().getId() : null)
                .itemTypeName(item.getItemType() != null ? item.getItemType().getName() : null)
                .specifications(item.getSpecifications())
                .estimatedValue(item.getEstimatedValue())
                .valueVarianceRatio(item.getValueVarianceRatio())
                .condition(item.getCondition())
                .tradeRange(item.getTradeRange())
                .status(item.getStatus())
                .createdAt(item.getCreatedAt())
                .updatedAt(item.getUpdatedAt() != null ? item.getUpdatedAt() : item.getCreatedAt())
                .build();
    }
}
