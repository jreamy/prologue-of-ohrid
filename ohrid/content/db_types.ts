
export default interface Content {
    [propName: string]: Reading
}

interface Reading {
    saints: Saint[];
    hymn_of_praise: Hymn;
    reflection: Reflection;
    contemplation: Contemplation;
    homily: Homily;
}

interface Saint {
    title: string;
    data: string[];
}

interface Hymn {
    title: string[];
    data: string[];
}

type Reflection = string[];

interface Contemplation {
    title: string;
    data: string[];
}

interface Homily {
    title: string;
    quote: string;
    data: string[];
}