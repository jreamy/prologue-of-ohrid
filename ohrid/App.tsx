/**
 * Sample React Native App
 * https://github.com/facebook/react-native
 *
 * @format
 */

import React, {useState} from 'react';
import {
  Button,
  SafeAreaView,
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  useColorScheme,
  View,
} from 'react-native';

import { Colors } from 'react-native/Libraries/NewAppScreen';

import database from './content/database'

const months = [
  "january", "february", "march", "april", "may", "june", "july", 
  "august", "september", "october", "november", "december"
]

function App(): JSX.Element {
  const isDarkMode = useColorScheme() === 'dark';

  const backgroundStyle = {
    backgroundColor: isDarkMode ? Colors.darker : Colors.lighter,
    color: isDarkMode ? Colors.light : Colors.dark,
  };

  const [date, setDate] = useState(new Date());

  let next_date = () => {
    let d = new Date(date);
    d.setDate(d.getDate() + 1);
    setDate(d);
  }

  let prev_date = () => {
    let d = new Date(date);
    d.setDate(d.getDate() - 1);
    setDate(d);
  }

  let data = database[months[date.getMonth()] + "-" + date.getDate() + ".json"];

  return (
    <View style={backgroundStyle}>
      <StatusBar
        barStyle={isDarkMode ? 'light-content' : 'dark-content'}
        backgroundColor={backgroundStyle.backgroundColor}
      />
      <SafeAreaView>
        <ScrollView>
          { /* date header */ }
          <View style={styles.sectionHeader}>
            <Button 
              onPress={prev_date}
              color={isDarkMode ? Colors.dark : Colors.light}
              title="prev"
            />
            <Text style={styles.sectionDate}>{date.toLocaleString('default', { month: 'long' })} {date.getDate()}</Text>
            <Button 
              onPress={next_date}
              color={isDarkMode ? Colors.dark : Colors.light}
              title="next"
            />
          </View>
          { /* lives of saints */ }
          <View key={date+"lives_of_saints"}>
            <Text style={styles.sectionTitle}>Lives of the Saints</Text>
            {data.saints.map(({title, data}) => (<View key={title}>
              <Text style={styles.subsectionTitle}>{title}</Text>
              {data.map((paragraph: string) => (
                <Text style={styles.text} key={paragraph}>{paragraph}</Text>
              ))}
            </View>))}
          </View>
          { /* hymn of praise */ }
          <View key={date+"hymn_of_praise"}>
            <Text style={styles.sectionTitle}>Hymn of Praise</Text>
            {data.hymn_of_praise.title.map((title: string) => (
              <Text style={{
                textAlign: 'center',
                ...styles.subsectionTitle
              }} key={title}>{title}</Text>
            ))}
            {data.hymn_of_praise.data.map((line: string) => (
              <Text style={styles.hymn_line} key={line}>{line}</Text>
            ))}
          </View>
          { /* reflection */ }
          <View key={date+"reflection"}>
            <Text style={styles.sectionTitle}>Reflection</Text>
            {data.reflection.map((paragraph: string) => (
              <Text style={styles.text} key={paragraph}>{paragraph}</Text>
            ))}
          </View>
          { /* contemplation */ }
          <View key={date+"contemplation"}>
            <Text style={styles.sectionTitle}>Contemplation</Text>
            <Text style={styles.subsectionTitle}>{data.contemplation.title}</Text>
            {data.contemplation.data.map((paragraph: string) => (
              <Text style={styles.text} key={paragraph}>{paragraph}</Text>
            ))}
          </View>
          { /* homily */ }
          <View key={date+"homily"}>
            <Text style={styles.sectionTitle}>Homily</Text>
            <Text style={styles.subsectionTitle}>{data.homily.title}</Text>
            <Text style={styles.subsectionTitle}>{data.homily.quote}</Text>
            {data.homily.data.map((paragraph: string) => (
              <Text style={styles.text} key={paragraph}>{paragraph}</Text>
            ))}
          </View>
          { /* navigation footer */ }
          <View style={styles.sectionHeader}>
            <Button 
              onPress={prev_date}
              color={isDarkMode ? Colors.dark : Colors.light}
              title="prev"
            />
            <Button 
              onPress={next_date}
              color={isDarkMode ? Colors.dark : Colors.light}
              title="next"
            />
          </View>
          <Text></Text>
        </ScrollView>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: StatusBar.currentHeight,
  },
  button: {
    zIndex: 0.5,
    borderRadius: 8,
    padding: 6,
  },
  sectionHeader: {
    paddingTop: 40,
    flexDirection: "row",
    alignSelf: 'center',
    alignItems: 'center',
  },
  sectionDate: {
    paddingLeft: 36,
    paddingRight: 36,
    fontSize: 36,
    fontWeight: '600',
    textAlign: 'center',
  },
  sectionTitle: {
    padding: 20,
    fontSize: 24,
    fontWeight: '600',
    textAlign: 'center',
  },
  subsectionTitle: {
    paddingLeft: 20,
    paddingRight: 20,
    fontSize: 20,
    fontWeight: '500',
    marginVertical: 8,
  },
  text: {
    paddingLeft: 24,
    paddingRight: 24,
    fontSize: 16,
    marginVertical: 2,
  },
  hymn_line: {
    paddingLeft: 10,
    paddingRight: 10,
    marginVertical: 2,
    fontSize: 16,
    textAlign: 'center',
  },
});

export default App;
