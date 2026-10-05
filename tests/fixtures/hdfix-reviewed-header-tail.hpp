



inline const std::initializer_list<std::string> kLauncherConfigCtrlTypes = { //THESE ARE ORDER SENSITIVE.
    ConfigKeys::ControllerType_PS5,          //0
    ConfigKeys::ControllerType_PS4,             //1
    ConfigKeys::ControllerType_XboxOne,         //2
    ConfigKeys::ControllerType_NintendoSwitch,  //3
    ConfigKeys::ControllerType_SteamDeck,       //4
    ConfigKeys::ControllerType_KeyboardMouse,   //5
    ConfigKeys::ControllerType_PS2,             //6 - custom, use ovr_ps2 folder.
};

inline const std::initializer_list<std::string> kLauncherConfigCtrlTypesInternal = { // !!! KEEP IN SYNC WITH THE LIST ABOVE !!!
    "PS5",
    "PS4",
    "XBOX",
    "NX",
    "STMD",
    "KBD",
    "PS4" //intentional for PS2, we override the ovr_ps4 folder to search for ovr_ps2 instead.
};

struct Game_Language_Pair_View
{
    std::string_view Region_Name;
    std::string_view Language_Name;
    std::string_view Game_Region;
    std::string_view Game_Language;
};

//Config Tool -> iTargetGame = TARGET_GAME_MGS3;
inline constexpr std::array<Game_Language_Pair_View, 9> MGS3_LanguagePairs =
{ {
    { "North America", "English",   "us", "en" },
    { "North America", "French",    "us", "fr" },
    { "North America", "Spanish",   "us", "sp" },
    { "Europe",        "English",   "eu", "en" },
    { "Europe",        "French",    "eu", "fr" },
    { "Europe",        "Italian",   "eu", "it" },
    { "Europe",        "German",    "eu", "gr" },
    { "Europe",        "Spanish",   "eu", "sp" },
    { "Japan",         "Japanese",  "jp", "jp" }
} };

//Config Tool -> iTargetGame = TARGET_GAME_MG1
//Config Tool -> iTargetGame = TARGET_GAME_MGS2
inline constexpr std::array<Game_Language_Pair_View, 6> MG1_MG2_MGS2_LanguagePairs =
{ {
    { "US / EU", "English",  "eu", "en" },
    { "US / EU", "French",   "eu", "fr" },
    { "US / EU", "Italian",  "eu", "it" },
    { "US / EU", "German",   "eu", "gr" },
    { "US / EU", "Spanish",  "eu", "sp" },
    { "Japan",   "Japanese", "jp", "jp" }
} };

template <size_t N>
static bool IsValidRegionLanguagePair(const std::array<Game_Language_Pair_View, N>& pairs, std::string_view region, std::string_view language)
{
    for (const auto& p : pairs)
    {
        if (p.Game_Region == region && p.Game_Language == language) return true;
    }
    return false;
}

template <size_t N>
static bool ResolveRegionLanguageNames(const std::array<Game_Language_Pair_View, N>& pairs, std::string_view game_region, std::string_view game_language, std::string& out_region_name, std::string& out_language_name)
{
    for (const auto& p : pairs)
    {
        if (p.Game_Region != game_region)
        {
            continue;
        }

        if (p.Game_Language != game_language)
        {
            continue;
        }

        out_region_name.assign(p.Region_Name);
        out_language_name.assign(p.Language_Name);
        return true;
    }

    return false;
}

constexpr int k3rdPersonMaxCameraDistance = 10000;
constexpr int k3rdPersonMinCameraDistance = 100;
constexpr int k3rdPersonFreecamDefaultMaxCameraDistance = 4000;
constexpr float k3rdPersonFreecamDefaultHorizontalSensitivity = 0.6f;
constexpr float k3rdPersonFreecamDefaultVerticalSensitivity = 0.4f;
